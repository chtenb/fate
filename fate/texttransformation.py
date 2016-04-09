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


### Multiple non-adjacent substitutions.
All intervals should compensate for the intervals difference in size of the interval before
them. Adjacent substitutions shouldn't complicate this much. The position that the two
substitutions have in common should be mapped to the same image anyway.


### Overlapping substitutions.
If there are overlapping substitutions available on the same text, it is unclear what the
textual result should be. So we pick the biggest.


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

The way the ambiguous position mappings are treated should be specified at creation time.
Potentially, regardless of whether this is useful, this specified behaviour can be
overridden at application time.

There are 4 sane behaviours to be distinghuished. Suppose we want to map interval [x,y] and
position x happens to be mapped to (a,b) using a map f.

1. Position a is always used.
2. Position b is always used.
3. The one that is closest to (either of) f(y) is used.
4. The one that is furthest from (either of) f(y) is used.

For cases 1 and 2 a mapping to a single positions should be used instead. So that leaves
us with two possible behaviours. So a flag indicating which behaviour should be used must
be specified along with the pair of positions.


### Transforming parts of a text
It should be easy to only transform a part of a text. Restrict all substitutions to one
interval in the text. For the mapping this means that all positions before that interval are
mapped to them selves and all positions after the interval are compensated for the difference
in size of the transformed part of the text.

"""

from enum import Enum
from typing import Iterable, List

from .selection import Interval


class MappingBehaviour:
    closest = 1
    furthest = 2


class IntervalSubstitution:

    def __init__(self, interval: Interval, new_length: int, behaviour:
            MappingBehaviour=MappingBehaviour.furthest):
        """
        :interval: the interval that is substituted.
        :new_length: the length of the resulting interval, after the substitution.
        :behaviour: how intervals should be mapped in the face of ambiguity. Only relevant when
        """
        self.interval = interval
        self.new_length = new_length
        self.behaviour = behaviour


class IntervalMapping:

    """Maps intervals accross a text transformation."""

    def __init__(self, textlength: int, mapping_start: int, mapping_end: int, substitutions:
            List[IntervalSubstitution]):
        """
        textlength: length of the text before the transformation.
        mapping_start/mappping_end: interval to which the transformation is restricted.
        substitutions: sorted (ascending by interval) list of IntervalSubstitutions. Interval
        are not allowed to overlap. Intervals are allowed to be adjacent.
        """
        self._textlength = textlength
        self._mapping_start = mapping_start
        self._mapping_end = mapping_end
        self._substitutions = substitutions

        assert mapping_start <= mapping_end
        # TODO: check sortedness of substitutions
        # TODO: check mutual exclusiveness of substitutions

        mapping = []
        # The last position that was mapped
        # NOTE: since adjacency is handled well in the code below, we acutally don't have to subtract 1
        orig_pos = mapping_start - 1 # can be -1
        # The last position that was being mapped to
        imag_pos = mapping_start - 1 # can be -1
        for substitution in substitutions:
            beg, end = substitution.interval

            if beg - orig_pos == 0:
                # Current substitution is adjacent to the previous
                pass
            else:
                orig_pos += 1
                imag_pos += 1

                # NOTE: From here, orig_pos and imag_pos are the next positions to be mapped

                # Map the untouched positions until the substitution
                nr_untouched_positions = beg - orig_pos # Including orig_pos, exluding beg
                mapping.extend(range(imag_pos, imag_pos + nr_untouched_positions)) # Exluding beg
                orig_pos += nr_untouched_positions # orig_pos is now at beg
                imag_pos += nr_untouched_positions # imag_pos is now at the position which will
                                                   # correspond to beg

            # Map the positions in the substitution
            old_length = end - beg
            new_length = substitution.new_length
            if old_length == 0:
                mapping.append((imag_pos, imag_pos + new_length, substitution.behaviour))
                imag_pos += new_length
            else:
                mapping.extend([imag_pos] * (old_length - 1))
                imag_pos += new_length
                mapping.append(imag_pos)

            # NOTE: From here, orig_pos and imag_pos are the last positions that were mapped

        # Map the remaining part
        nr_remaining_positions = mapping_end - orig_pos
        mapping.extend(range(imag_pos, imag_pos + nr_remaining_positions))


