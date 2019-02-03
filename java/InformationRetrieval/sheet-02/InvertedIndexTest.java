
// Copyright 2017 University of Freiburg
// Christian Breu <Breuch@web.de>
// Michael Zinner <zinnermichael@live.com>

import java.util.AbstractMap;
import java.util.AbstractMap.SimpleEntry;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

import org.junit.Assert;
import org.junit.Test;

/**
 * One unit test for each non-trivial method in the InvertedIndex class.
 */
public class InvertedIndexTest {
  /**
   * Tests for the method readFromFile().
   */

  @Test
  public void testReadFromFile() {

    InvertedIndex ii = new InvertedIndex();
    ii.readFromFile("example.txt", 0,
        Double.POSITIVE_INFINITY);

    // Test case 1(from TIP)
    Map<String, List<AbstractMap.SimpleEntry<Integer,
        Double>>> sortedLists = new TreeMap<>(
        ii.invertedLists);

    Assert.assertEquals(
        "{animated=[1=0.415, 2=0.415, 4=0.415], animation=[3=2.0],"
            + " film=[2=1.0, 4=1.0],"
            + " movie=[1=0.0, 2=0.0, 3=0.0, 4=0.0], non=[2=2.0], "
            + "short=[3=1.0, 4=2.0]}",
        sortedLists.toString());
    // Test case 2(from TIP)
    ii = new InvertedIndex();
    ii.readFromFile("example.txt", 0.75, 1.75);

    Map<String, List<AbstractMap.SimpleEntry<Integer,
        Double>>> sortedLists2 = new TreeMap<>(
        ii.invertedLists);
    Assert.assertEquals(
        "{animated=[1=0.459, 2=0.402, 4=0.358], animation=[3=2.211],"
            + " film=[2=0.969, 4=0.863],"
            + " movie=[1=0.0, 2=0.0, 3=0.0, 4=0.0], non=[2=1.938],"
            + " short=[3=1.106, 4=1.313]}",
        sortedLists2.toString());
  }

  @Test
  public void testMerge() {
    List<SimpleEntry<Integer, Double>> testList1 = new ArrayList<SimpleEntry
        <Integer, Double>>();
    testList1.add(new SimpleEntry<Integer, Double>(1, 2.1));
    testList1.add(new SimpleEntry<Integer, Double>(5, 3.2));
    List<SimpleEntry<Integer, Double>> testList2 = new ArrayList<SimpleEntry
        <Integer, Double>>();
    testList2.add(new SimpleEntry<Integer, Double>(1, 1.7));
    testList2.add(new SimpleEntry<Integer, Double>(2, 1.3));
    testList2.add(new SimpleEntry<Integer, Double>(5, 3.3));

    // Test case from TIP
    InvertedIndex ii = new InvertedIndex();
    testList1 = ii.merge(testList1, testList2);
    Assert.assertEquals("[1=3.8, 2=1.3, 5=6.5]", testList1.toString());

  }

  @Test
  public void testProcess_query() {
    // create testLists
    List<SimpleEntry<Integer, Double>> testListFoo = new ArrayList<SimpleEntry
        <Integer, Double>>();
    testListFoo.add(new SimpleEntry<Integer, Double>(1, 0.2));
    testListFoo.add(new SimpleEntry<Integer, Double>(3, 0.6));
    List<SimpleEntry<Integer, Double>> testListBar = new ArrayList<SimpleEntry
        <Integer, Double>>();
    testListBar.add(new SimpleEntry<Integer, Double>(1, 0.4));
    testListBar.add(new SimpleEntry<Integer, Double>(2, 0.7));
    testListBar.add(new SimpleEntry<Integer, Double>(3, 0.5));
    List<SimpleEntry<Integer, Double>> testListBaz = new ArrayList<SimpleEntry
        <Integer, Double>>();
    testListBaz.add(new SimpleEntry<Integer, Double>(2, 0.1));

    // Test case from TIP
    InvertedIndex ii = new InvertedIndex();
    ii.invertedLists.put("foo", testListFoo);
    ii.invertedLists.put("bar", testListBar);
    ii.invertedLists.put("baz", testListBaz);
    testListFoo = ii.process_query("foo bar");
    Assert.assertEquals("[3=1.1, 2=0.7, 1=0.6]", testListFoo.toString());

  }

}