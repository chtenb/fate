"""
A text transformation is an operation which converts one text to another. Trivially, one can
define and store such a transformation as just the original text and the image. But this throws
away information about the transformation and it is a waste of space. We only want to consider
the difference between two texts as a transformation. This reduces a transformation to a set of
substitutions within a text.

We want to be able to carry over intervals from the original text to the image of the
transformation. So a text transformation must also define a mapping of intervals across the
transformation. When we need to map individual positions, we can derive this from the interval
mapping by mapping an empty interval at the position and then take the lower position of the
output interval. In general, however, we can not just map positions and derive from that how
intervals should be mapped, as we will see later on.


### Substitutions of length 1
To investigate this aspect further, let us for now restrict ourselves to transformations of
length at most 1. We can distinguish three cases here. We do not try to minimize the number of
cases or make them mutually exclusive. Our aim is to make it clear how intervals should be
mapped and evident that out approach is exhaustive.

1. Deletion of a character.
    Suppose a character is deleted between position x and x+1. Then affected intervals
    should be mapped as follows.
    [a,x] => [a,x]
    [a,x+1] => [a,x]
    [x,a] => [x,a-1]
    [x+1,a] => [x,a-1]
    and so [x,x+1] => [x,x]
    For the remaining intervals the positions should just compensate for the difference in
    size.

2. Insertion of a character.
    Suppose a character is inserted at position x. Then affected intervals should be
    mapped as follows.
    [a,x] => [a,x] or [a,x+1]
    [x,a] => [x,a+1] or [x+1,a+1]
    and so [x,x] => [x,x] or [x,x+1] or [x+1,x+1]
    For the remaining intervals the positions should just compensate for the difference in
    size.

3. Substitution of a character with another character.
    Suppose a character is substituted between position x and x+1.
    Nothing really changes. So affected intervals should be mapped as follows.
    [a,x] => [a,x]
    [a,x+1] => [a,x+1]
    [x,a] => [x,a]
    [x+1,a] => [x+1,a]
    and so [x,x+1] => [x,x+1]

IMPORTANT:
In case 2, for some applications we might want to map
    [a,b] => { [a,x], [x+1,b] }
But since this is quite a specific use case and complicates everything even more, we want to
leave this for now, and implement it in a dedicated type of transformation.

For case 2, a choice must be made for all kind of affected intervals.  Note that for the
inverse, the deletion becomes an insertion, and as such, again a choice must be made.  This
choice should be made at creation time, since at execution time the context and semantics of a
certain substitution is not known.


### Substitutions of arbitrary length
We can distinguish three cases here.
1. Deletion of a character.
    Suppose a sequence of characters is deleted between position x and x+s.
    Then affected intervals should be mapped as follows.
    [a,x+y] => [a,x], for all 0 <= y <= s
    [x+y,a] => [x,max(x,a-s)], for all 0 <= y <= s
    and so [x,x+s] => [x,x]
    For the remaining intervals the positions should just compensate for the difference in
    size.

2. Insertion of a character.
    Suppose a range of characters of length s is inserted at position x. Then affected
    intervals should be mapped as follows.
    [a,x] => [a,x] or [a,x+s]
    [x,a] => [x,a+s] or [x+s,a+s]
    and so [x,x] => [x,x] or [x,x+s] or [x+s,x+s]
    For the remaining intervals the positions should just compensate for the difference in
    size.

3. Substitution of a character with another character.
    Suppose the characters between position x and x+s are replaced with t characters,
    0 < t and s < 0.  Then affected intervals should be mapped as follows.
    [x,a] => [x,a-s+t]
    [a,x+s] => [a,x+t]
    [a,x+y] => [a,x] or [a,x+t], for all 1 <= y <= s-1
    [x+y,a] => [x,a-s+t] or [x+t,a-s+t], for all 1 <= y <= s-1
    and so [x,x+s] => [x,x+t]
    For the remaining intervals the positions should just compensate for the difference in
    size.

Why do we only allow ambiguous interval end points to be mapped to endpoints of the
substitution? Because we cannot know of any relation between characters inside the
substitution operands. If some substitution wanted to expose such information, the
substitution should be chopped down into finer substitutions such that related characters
or substrings are exactly mapped onto each other.

Again we see that choice has to be made in some situations. Let's do it.
For insertions we want to map
[x,x] => [x,x+s]
[a,x] => [a,x]
[x,a] => [x+s,a+s]
since otherwise intervals can end up being overlapping each other, which we want to avoid.
I.e. we want intervals that are disjoint to remain disjoint after being taken accross the
mapping.
For substitutions we want to map
[a,x+y] => [a,x], for all 1 <= y <= s-1, a <= x
[x+y,a] => [x+t,a-s+t], for all 1 <= y <= s-1, x <= a
[x+y,x+z] => [x,x], for all 1 <= y <= z <= s-1
for the same reason.


### Multiple substitutions.
All intervals should compensate for the intervals difference in size of the interval before
them. Adjacent substitutions shouldn't complicate this much. The position that the two
substitutions have in common should be mapped to the same image anyway.  If there are
overlapping substitutions available on the same text, it is unclear what the textual result
should be. So we pick the biggest or we just forbid it.  What if multiple insertions are done
at the same position? It is not really clear if this falls under overlapping substitutions. We
can either merge them to be a single insertion or forbid them.


### Composition of transformations.
We don't need to be able to construct a single transformation from a chain of transformations.
We can just apply the mappings and substitutions sequentially when we need to take something
accross multiple transformations.


### Inversion of transformations. What are the algebraic properties?
It is very convenient for transformations to be fully invertible, in the sense that applying
and undoing any transformation always ends up with the exact same situation as before.
It is clear how we should invert insertion and replacement of a single character. What
about deletion?  A deletion is not invertible, since two positions are merged into one.
For any interval having at least one of these two positions as end point, it will be
unclear how to invert the mapping without extra information.


### How to create a transformation between two texts?
E.g. for after formatting by external programs.  There exist several difference algorithms
for this, each with its own downsides.  We don't need to have this in the core at the
moment, so we can leave this be.


### Storing the mapping efficiently for speed and storage.
Naively mapping all intervals explicitly will result in O(n^2) storage and performance,
where n is the length of the text. This is unacceptable, since these transformations have
to be done multiple times per keypress. It should be possible to optimize this to n being
the length of the screen, but still.

Untouched positions and endpoints of substitutions and deletions can just be mapped
straight away. The position at an insertion should be mapped to two other positions and
should be treated special. The inner positions of a substitutions of length > 1 should
also be mapped to two other positions, and be treated special as well.

### Transforming parts of a text
It should be easy to only transform a part of a text. Restrict all substitutions to one
interval in the text. For the mapping this means that all positions before that interval are
mapped to them selves and all positions after the interval are compensated for the difference
in size of the transformed part of the text.

###TODO
Be able to apply text trasnformations on part of texts (i.e. just the part the is on the
screen) for performance reasons. This is closely related to implementing a faster text
datastructure for large texts.
"""

from typing import List, Any
from copy import copy

from typedecorator import typed

from .selection import Interval, Selection
from .text import Text


class IntervalSubstitution:

    def __init__(self, interval: Interval, new_length: int):
        """
        :interval: the interval that is substituted.
        :new_length: the length of the resulting interval, i.e. end - beg, after the substitution.
        """
        self.interval = interval
        self.new_length = new_length

    def __repr__(self):
        return '{}: {}'.format(self.interval, self.new_length)

    @property
    def is_insertion(self):
        return self.interval.isempty


class IntervalMapping:

    """Maps intervals accross a text transformation."""

    def __init__(self, substitutions: List[IntervalSubstitution]):
        """
        substitutions: sorted (ascending by interval) list of IntervalSubstitutions. Interval
        are not allowed to overlap. Intervals are allowed to be adjacent. It is not allowed to
        have multiple insertions at the same position.
        """
        # Remove insertions of length 0
        substitutions = [s for s in substitutions if not (
            s.is_insertion and s.new_length == 0)]

        # Deduce mapping_start/mapping_end from the substitutions. If something must be
        # restricted for reasons of speed, the substitutions themselves must be restricted.
        # Also, this method is already complex enough. We don't have to replace the
        # mappingstart/end arguments with a single length argument, since we can just treat any
        # position larger than the last substitution the same way.

        # mapping_start: inclusive lower bound to which the transformation is restricted.
        # mappping_end: inclusive upper bound to which the transformation is restricted.
        if not substitutions:
            mapping_start = 0
            mapping_end = 0
        else:
            mapping_start = substitutions[0].interval[0]
            mapping_end = substitutions[-1].interval[1]

        self._mapping_start = mapping_start
        self._mapping_end = mapping_end
        self._substitutions = substitutions

        assert mapping_start <= mapping_end

        # PROBLEM:
        # If we map the first position of the next substitution already, we can't do
        # insertions. If we don't map the first position of the next substitution, we have an
        # extra case for when substitutions are adjacent, since in that case the first position
        # of the next substitution is part of the substitution before that.
        # SOLUTION:
        # Map the first position of the next substitution, and insertions always replace the
        # last element in the mapping.

        # The mapping from original positions to their image.
        mapping = [mapping_start]
        # The last position that was mapped
        orig_pos = mapping_start
        # The last position that was mapped to
        imag_pos = mapping_start
        previous_substitution = None
        for substitution in substitutions:
            beg, end = substitution.interval

            # Check sortedness of substitutions and mutual exclusiveness of substitutions
            if previous_substitution != None:
                assert previous_substitution.interval[1] <= beg

            if beg - orig_pos == 0:
                # Current substitution is adjacent to the previous
                pass
            else:
                # Map the untouched positions until the substitution.  We want map the first
                # position of the current substitution as well to make sure that we end up in
                # the same case as when current substitution is adjacent to the previous.

                # Don't count orig_pos (already been mapped) and count beg
                nr_untouched_positions = beg - orig_pos
                # Map imag_pos up to (and including) beg
                mapping.extend(range(imag_pos + 1,
                                     imag_pos + 1 + nr_untouched_positions))
                # Let orig_pos be at beg + 1
                orig_pos += nr_untouched_positions
                # Let imag_pos be at the position which beg is going to be mapped to
                imag_pos += nr_untouched_positions

            # NOTE: the first position of our substitution is already mapped
            assert orig_pos == beg

            # Map the positions in the substitution
            # Don't count beg (already been mapped) and count end
            old_length = end - beg
            new_length = substitution.new_length
            if old_length == 0:
                # We replace the last value
                if mapping and isinstance(mapping[-1], tuple):
                    # If previous substitution was an insertion as well, merge with it
                    mapping[-1] = (mapping[-1][0], imag_pos + new_length)
                else:
                    mapping[-1] = (imag_pos, imag_pos + new_length)
            else:
                mapping.extend([imag_pos] * (old_length - 1))
                mapping.append(imag_pos + new_length)

            orig_pos += old_length  # we mapped up to and including (orig_pos + old_length)
            imag_pos += new_length  # we mapped up to and including (imag_pos + new_length)
            previous_substitution = substitution

        # Map the remaining part
        nr_remaining_positions = mapping_end - orig_pos
        mapping.extend(range(imag_pos + 1, imag_pos + 1 + nr_remaining_positions))

        assert mapping_end - mapping_start + 1 == len(mapping), '{} - {} != len({})'.format(
            mapping_end, mapping_start, mapping)

        self._innermapping = mapping

    def __getitem__(self, item: (int, Interval, Selection)) -> (int, Interval, Selection):
        """
        :item: position, interval or selection to map.
        """
        mapping = self._innermapping
        mapping_start = self._mapping_start
        mapping_end = self._mapping_end

        if isinstance(item, Selection):
            selection = item
            result = Selection()
            for interval in selection:
                result.add(self[interval])
            return result

        if isinstance(item, Interval):
            interval = item
            beg, end = interval
            if (interval.isempty and mapping_start <= beg <= mapping_end
                    and isinstance(mapping[beg - mapping_start], tuple)):
                return Interval(*mapping[beg - mapping_start])
            else:
                return Interval(self._map_position(beg, False), self._map_position(end, True))

        return self._map_position(item, True)

    def _map_position(self, position: int, snap_down: bool) -> int:
        """
        :position: position to map.
        :snap_down: if True, return the lowest candidate position, otherwise the highest.
        """
        mapping = self._innermapping
        mapping_start = self._mapping_start
        mapping_end = self._mapping_end

        if position < self._mapping_start:
            return position
        elif position > self._mapping_end:
            codomain_start = mapping[0] if isinstance(mapping[0], int) else mapping[0][0]
            codomain_end = mapping[-1] if isinstance(mapping[-1], int) else mapping[-1][1]
            len_codomain = codomain_end - codomain_start + 1
            len_diff = len_codomain - len(mapping)
            result = position + len_diff
            assert result >= 0
            return result

        assert mapping_start <= position <= mapping_end
        result = mapping[position - mapping_start]
        if isinstance(result, tuple):
            if snap_down:
                return result[0]
            else:
                return result[1]
        return result

    def __repr__(self):
        return repr(self._innermapping)


class TextTransformation:

    """Transforms a text and maps positions accross this transformation."""

    def __init__(self: 'TextTransformation', selection: Selection, replacements: List[str], text: Text):
        """
        :selection: selection for which the intervals get new content.
        :replacements: sorted (ascending by interval) list of strings representing the new
        content of the intervals in the selection.

        Interval are not allowed to overlap. Intervals are allowed to be adjacent. It is
        allowed to have multiple insertions at the same position.
        """
        assert isinstance(text, Text)
        self.selection = selection
        self.replacements = replacements

        substitutions = [IntervalSubstitution(selection[i], len(replacements[i]))
                         for i in range(len(selection))]
        self.intervalmapping = IntervalMapping(substitutions)

        # Store some information to be able to construct an inverse
        self.validate(text)
        self.original_content = self.selection.content(text)

    def compute_newselection(self):
        """The selection containing the potential result of the operation."""
        return Selection([self.intervalmapping[interval] for interval in self.selection])

    def validate(self: 'TextTransformation', text: 'Text'):
        """
        Make sure the application of this operation is valid at this moment
        """
        assert isinstance(text, Text)
        self.selection.validate(text)
        newselection = self.compute_newselection()
        assert len(newselection) == len(self.selection)
        # This is not true in case of multiple insertions at the same position
        # content = self.selection.content(text)
        # assert len(self.replacements) == len(content)

    def inverse(self, text):
        """
        Return the inverse transformation.  The selection of the inverse is the selection of
        the result of the current transformation.  The replacements of the inverse are simply
        the contents of the selection of the current transformation.
        """
        inverse_selection = self.compute_newselection()
        inverse_replacements = copy(self.original_content)
        return TextTransformation(inverse_selection, inverse_replacements, text)


class PartialTextTransformation(TextTransformation):

    """
    Text transformation which limits the substitutions being done to a certain interval.
    Can be used in conjunction with PartialText for performance reasons to compute the text
    that is viewed on the screen by the user.
    """

    def __init__(self, original_transformation: TextTransformation, beg: int, end: int, text):
        assert isinstance(text, Text)
        self.origin = original_transformation
        self.beg = beg
        self.end = end
        self.interval = Interval(beg, end)

        # Exclude substitutions that are not within our range
        intervals = []
        replacements = []
        for i, interval in enumerate(original_transformation.selection):
            if interval in self.interval:
                intervals.append(interval)
                replacements.append(original_transformation.replacements[i])
        selection = Selection(intervals)

        TextTransformation.__init__(self, selection, replacements, text)

