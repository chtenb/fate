"""
A text transformation is an operation which converts one text to another. Trivially, one
can define and store such a transformation as just the original text and the image. But
this throws away information about the transformation and it is a waste of space. We only
want to consider the difference between two texts as a transformation. This reduces a
transformation to a set of substitutions within a text.

We want to be able to carry over intervals from the original text to the image of the
transformation. So a text transformation must also define a mapping of intervals across
the transformation.

Let us restrict ourselves to transformations of length at most 1. We can distinguish three
cases here.
1. Deletion of a character.
    Suppose a character is deleted between position x and x+1. Then affected intervals should
    be mapped as follows.
    [a,x] => [a,x]
    [a,x+1] => [a,x]
    [x,a] => [x,a-1]
    [x+1,a] => [x,a-1]

2. Insertion of a character.
    Suppose a character is inserted at position x. Then affected intervals should be
    mapped as follows.
    [a,x] => [a,x] or [a,x+1]
    [x,a] => [x,a+1] or [x+1,a+1]

    And so
    [x,x] => [x,x] or [x,x+1] or [x+1,x+1]

3. Substitution of a character with another character.
    Suppose a character is substituted between position x and x+1.
    Nothing really changes. So affected intervals should be mapped as follows.
    [a,x] => [a,x]
    [a,x+1] => [a,x+1]
    [x,a] => [x,a]
    [x+1,a] => [x+1,a]


For case 2, a choice should be made at substitution time for all kind of affected intervals.

There are some extensions to be investigated yet.
- Transformations of greater length.
- Multiple transformations.
- Adjacent transformations.
- Can one of the cases be defined in terms of the other?
- How to create a transformation between two texts? E.g. for after formatting by external
  programs.
"""
