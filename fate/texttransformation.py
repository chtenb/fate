"""
A text transformation is an operation which converts one text to another. Trivially, one can
define and store such a transformation as just the original text and the image. But this throws
away information about the transformation and it is a waste of space. We only want to consider
the difference between two texts as a transformation. This reduces a transformation to a set of
substitutions within a text.

Note that it is possible to define other kinds of transformations that are not fully
expressable as a set of substitutions in the text. For instance, the transformation formed by
reversing the text is not really expressable in terms of substitutions while keeping the
information about which position was mapped to which other position. But since there is not a
clear and relevant application for these kind of transformations, we restrict ourselves to
transformations formed by substitutions.

We want to be able to carry over selections from the original text to the image of the
transformation. So a text transformation must also define some sort of mapping of intervals
across the transformation. When we need to map individual positions, we can derive this from
the interval mapping by mapping an empty interval at the position and then take the lower
position of the output interval. In the implementation, however, we can not just map positions
and derive from that how intervals should be mapped, as we will see later on.


### Mathematical properties
Suppose M is a function that maps positions, intervals and selections accross a texttransformation.
Because only substitutions are allowed in this transformation, the following should hold.
Let a,b be positions.
1. a <= b  <==>  M(a) <= M(b) (order preserving)
Let (a,b) and (c,d) be intervals.
2. b <= c  <==>  M(b) <= M(c) (order preserving, disjointness preserving)

For selections we can simply map its individual intervals and form the result by putting the
resulting intervals in a selection. By the above properties, the resulting selection will
consist of disjoint intervals, and thus be a valid selection.

We cannot take this further, and simply map individual positions. This approach appears to be
not expressive enough for what we want to achieve. For example, if some text is inserted at a
certain position x, we want to be able to express that x maps to the interval containing this
newly inserted text. This is not possible if x were to map to a single position.

We will now list the possible mappings of intervals to their images in a way that they don't
conflict with other possible disjoint intervals in the same transformation.

### Substitutions of length 1
To investigate these transformations further, let us for now restrict ourselves to
substitutions of length at most 1 and see what possibilities we have of mapping intervals
affected by this substitution. We can distinguish three cases here. We do not try to minimize
the number of cases or make them mutually exclusive. Our aim is to make it clear how intervals
should be mapped and evident that our approach is exhaustive. We will list all possible ways of
mapping intervals that do not immiately conflict with other possible substitutions.

1. Deletion of a character.
    Suppose a character is deleted between position x and x+1. Then affected intervals
    should be mapped as follows.
    [a,x] => [a,x], for a < x
    [a,x+1] => [a,x], for a < x
    [x,a] => [x,a-1], for x+1 < a
    [x+1,a] => [x,a-1], for x+1 < a
    [x,x] => [x,x]
    [x,x+1] => [x,x]
    [x+1,x+1] => [x,x]
    [a,b] => [a,b-1], for a < x < x+1 < b

2. Insertion of a character.
    Suppose a character is inserted at position x. Then affected intervals should be
    mapped as follows.
    [a,x] => [a,x] or [a,x+1], for a < x
    [x,a] => [x,a+1] or [x+1,a+1], for x < a
    [x,x] => [x,x] or [x,x+1] or [x+1,x+1]
    [a,b] => { [a,x], [x+1,b+1] } or [a,b+1], for a < x < b

3. Substitution of a character with another character.
    Suppose a character is substituted between position x and x+1.
    So affected intervals should be mapped as follows.
    [a,x] => [a,x] or [a,x+1], for a < x
    [a,x+1] => [a,x+1] or [a,x], for a < x
    [x,a] => [x,a] or [x+1,a], for x+1 < a
    [x+1,a] => [x+1,a] or [x,a], for x+1 < a
    [x,x] => [x,x] or [x,x+1] or [x+1,x+1]
    [x,x+1] => [x,x], [x,x+1] or [x+1,x+1]
    [x+1,x+1] => [x,x] or [x,x+1] or [x+1,x+1]
    [a,b] => { [a,x], [x+1,b] } or [a,b], for a < x < x+1 < b

### Substitutions of arbitrary length

1. Deletion of a character.
    Suppose a sequence of characters is deleted between position x and x+s.
    Then affected intervals should be mapped as follows.
    [a,x+y] => [a,x], for all 0 <= y <= s, for a < x
    [x+y,a] => [x,a-s], for all 0 <= y <= s, for x+s < a
    any interval in [x,x+s] => [x,x]
    [a,b] => [a,b-s], for a < x < x+s < b

2. Insertion of a character.
    Suppose a range of characters of length s is inserted at position x. Then affected
    intervals should be mapped as follows.
    [a,x] => [a,x] or [a,x+s] or some in between, for a < x
    [x,a] => [x,a+s] or [x+s,a+s] or some in between for x < a
    [x,x] => some interval in [x,x+s]
    [a,b] => { [a,x], [x+s,b+s] } or [a,b+s], for a < x < x+s < b

3. Substitution of a character with another character.
    Suppose the characters between position x and x+s are replaced with t characters,
    0 < s,t.  Then affected intervals should be mapped as follows.
    [a,x+y] => [a,x+z], for some 0 <= z <= s, for all 0 <= y <= s
    [x+y,a] => [x+z,a], for some 0 <= z <= s, for all 0 <= y <= s
    some interval in [x,x+s] => some interval in [x,x+t]
    [a,b] => { [a,x], [x+s,b] } or [a,b], for a < x < x+s < b

### Making choices in the mapping

Sometimes a choice must be made between different images. This is not the case for deletions,
but note that for the inverse, the deletion becomes an insertion, and as such, again a choice
must be made.  This choice should probably be made at creation time, since at execution time the context
and semantics of a certain substitution may not be known.

It can be observed that not all combinations of choices satisfy mathematical property 2. We
want to rule out options that cause this property to be violated.

Moreover, we want to rule out all mappings that relate positions to other position that are
strictly inside the interval image.  This is because we cannot know of any relation between
characters inside the substitution operands. If some substitution wanted to expose such
information, the substitution should be chopped down into finer substitutions such that related
characters or substrings are exactly mapped onto each other.

This results in the following mapping templates.

For insertions we want to map
[a,x] => [a,x]
[x,a] => [x+s,a+s]
[x,x] => [x,x+s] or [x,x], depending on the type of insertion
[a,b] => [a,b+s] or { [a,x], [x+s,b+s] }, depending on the type of insertion
since otherwise intervals can end up being overlapping each other, which violates mathematical
property 2. Furthermore, we choose [x,x] over [x+s,x+s] for no clear reason.

By similar reasoning for substitutions we want to map
[a,x+y] => [a,x], for all 0 <= y <= s-1
[a,x+s] => [a,x+t] or [a,x], depending on the type of substitution
[x+y,a] => [x+t,a-s+t], for all 1 <= y <= s
[x,a] => [x,a-s+t] or [x+t,a-s+t], depending on the type of substitution
some interval strictly in [x,x+s] => [x,x]
[x,x+s] => [x,x+t] or [x,x], depending on the type of substitution
[a,b] => [a,b+s] or { [a,x], [x+s,b+s] }, depending on the type of substitution

Again we see that choice has to be made in some situations.
So a special kind of substitution is to be introduced, which determines whether the first
or the second options are chosen. Let's call the first option 'inclusive' and the second
'exclusive'.

--- TO BE CONTINUED HERE

### Multiple substitutions.
All mapped intervals should compensate for the positional difference caused by the
substitutions before them.
- If there are overlapping substitutions available on the same text, it is unclear what the
  textual result should be. So we forbid it.
- Adjacent substitutions complicate a little bit. Instead of having two candidate images,
  the common position has three candidates.
  Let x <= y <= z. Suppose [x,y] and [y,z] are substituted inducing the map M.
  If both substitutions are inclusive, y is always mapped to M(y).
  If both substitutions are exclusive, y is always mapped to M(x) or M(z).
  If [x,y] is substituted exclusively and [y,z] inclusively, y is mapped to M(y) if its part of
  an interval of the form [y,a]. If it is part of an interval of the form [a,y], y is mapped to
  M(x). And [y,y] should be mapped to [M(y), M(y)].
- What if multiple insertions are done at the same position x? The interval [x,x] is mapped to
  the selection containing all images of the insertions, taking the exclusiveness into account
  of course. All other intervals have nothing to do with this.
- Sometimes a specific ordering is required. E.g. an insertion on a new line together with a
  line number; the line number must go first. We must be able to express this. The ordering of
  the selection and the replacements when creating a TextTransformation, must be maintained.


### Inversion of transformations.
It is very convenient for transformations to be fully invertible, in the sense that applying
and undoing any transformation always ends up with the exact same situation as before.
It is clear how we should invert insertion and replacement of a single character. What
about deletion?  A deletion is not invertible, since two positions are merged into one.
For any interval having at least one of these two positions as end point, it will be
unclear how to invert the mapping without extra information.


### Storing the mapping efficiently for speed and storage.
Naively mapping all intervals explicitly will result in O(n^2) storage and performance,
where n is the length of the text. This is unacceptable, since these transformations have
to be done multiple times per keypress. It should be possible to optimize this to n being
the length of the screen, but still.

Untouched positions and endpoints of substitutions and deletions can just be mapped
straight away. The position at an insertion should be mapped to two other positions and
should be treated special. The inner positions of a substitutions of length > 1 should
also be mapped to two other positions, and be treated special as well.

An observation we make is that each position inside a substitution can map two either of two
candidate images, depending on the interval that is mapped and the type of substitution.
So we can map each position outside a substitution to a single image position, and each
position inside a substitution to a tuple of two positions, namely the two endpoints of the
replacement. There remains one thing to be described in the representation, namely whether a
substitution is inclusive or exclusive. We could subclass tuple and add a field which indicates
this. We also need an indication for whether such a tuple was caused by an insertion or not.
Although the latter can also be verified be checking this tuple has no similar neighbors.
The same holds for indicating if such a tuple is an endpoint, and which.

For storing multiple interval replacements at one position, we can simply use a list. This also
maintains information about the ordering of the insertions, which is required.


### Composition of transformations.
We don't need to be able to construct a single transformation from a chain of transformations.
We can just apply the mappings and substitutions sequentially when we need to take something
accross multiple transformations.



### How to create a transformation between two texts?
E.g. for after formatting by external programs.  There exist several difference algorithms
for this, each with its own downsides.  We don't need to have this in the core at the
moment, so we can leave this be.


### Transforming parts of a text
It should be easy to only transform a part of a text. Restrict all substitutions to one
interval in the text. For the mapping this means that all positions before that interval are
mapped to them selves and all positions after the interval are compensated for the difference
in size of the transformed part of the text.

"""

from typing import List, Any
from copy import copy

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


class PositionReplacement(Interval):

    def __new__(cls, beg, end, exclusive=False):
        """
        :beg: the beg of the interval that envelops this position replacement
        :end: the end of the interval that envelops this position replacement
        :exclusive: whether the substitution was exclusive. Default is inclusive.
        """
        tuple.__new__(cls, beg, end)

    def __init__(self, beg, end, exclusive=False):
        self.exclusive = exclusive

    def __repr__(self):
        if not self.exclusive:
            return Interval.__repr__(self)
        return 'excl' + Interval.__repr__(self)


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
