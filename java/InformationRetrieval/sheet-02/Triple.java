// Copyright 2017 University of Freiburg
// Christian Breu <breuch@web.de>
// Michael Zinner <zinnermichael@live.com>

/**
 * Helper class for EvaluateInvertedIndex
 */
public class Triple {

  private float first;
  private float second;
  private float third;

  /**
   * A triple of floats
   * @param first
   *          The first float
   * @param second
   *          The second float
   * @param third
   *          The third float
   */
  public Triple(float first, float second, float third) {
    this.first = first;
    this.second = second;
    this.third = third;
  }

  public float getFirst() {
    return first;
  }

  public void setFirst(float first) {
    this.first = first;
  }

  public float getSecond() {
    return second;
  }

  public void setSecond(float second) {
    this.second = second;
  }

  public float getThird() {
    return third;
  }

  public void setThird(float third) {
    this.third = third;
  }
}
