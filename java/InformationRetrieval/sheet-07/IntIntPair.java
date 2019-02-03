
// Copyright 2017, University of Freiburg,
// Chair of Algorithms and Data Structures.
// Author: Claudius Korzen <korzen@cs.uni-freiburg.de>.

/**
 * A pair consisting of two integer values.
 */
public class IntIntPair {
  /**
   * The first integer.
   */
  public int first;

  /**
   * The second integer.
   */
  public int second;

  /**
   * Creates a new pair that consists of two integer values.
   * 
   * @param first
   *        The first integer.
   * @param second
   *        The second integer.
   */
  public IntIntPair(int first, int second) {
    this.first = first;
    this.second = second;
  }

  @Override
  public String toString() {
    return String.format("(%d, %d)", this.first, this.second);
  }
}
