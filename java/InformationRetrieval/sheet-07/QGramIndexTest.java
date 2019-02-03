
// Copyright 2017, University of Freiburg,
// Chair of Algorithms and Data Structures.
// Author: Hannah Bast <bast@cs.uni-freiburg.de>,
// Claudius Korzen <korzen@cs.uni-freiburg.de>.

import static org.junit.Assert.assertEquals;

import java.io.UnsupportedEncodingException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import org.junit.Test;

/**
 * One unit test for each non-trivial method in the QGramIndex class.
 */
public class QGramIndexTest {

  /**
   * Tests for the constructor.
   */
  @Test
  public void testConstructor() {
    QGramIndex qgi = new QGramIndex(3, false);
    assertEquals(3, qgi.que);
    assertEquals("$$", qgi.padding);
    assertEquals("{}", qgi.invertedLists.toString());
  }

  /**
   * Tests for the method buildFromFile().
   */
  @Test
  public void testBuildFromFile() {
    QGramIndex qgi = new QGramIndex(3, false);
    qgi.buildFromFile("example.tsv");
    assertEquals("{$$b=[2], $$f=[1], $br=[2], $fr=[1], bre=[2], fre=[1], "
        + "rei=[1, 2]}", qgi.invertedLists.toString());
    assertEquals(
        "[Entity(name='frei', score=3, desc='a word'), "
            + "Entity(name='brei', score=2, desc='another word')]",
        qgi.entities.toString());
  }

  /**
   * Tests for the method mergeLists().
   */
  @Test
  public void testMergeLists() {
    List<Integer> first = Arrays.asList(1, 1, 3, 5);
    List<Integer> second = Arrays.asList(2, 3, 3, 9, 9);
    List<List<Integer>> lists = Arrays.asList(first, second);

    assertEquals("[(1, 2), (2, 1), (3, 3), (5, 1), (9, 2)]",
        QGramIndex.mergeLists(lists).toString());
  }

  /**
   * Tests for the method prefixEditDistance().
   */
  @Test
  public void testPrefixEditDistance() {
    assertEquals(0, QGramIndex.prefixEditDistance("frei", "frei", 0));
    assertEquals(0, QGramIndex.prefixEditDistance("frei", "freiburg", 0));
    assertEquals(1, QGramIndex.prefixEditDistance("frei", "breifurg", 1));
    assertEquals(3, QGramIndex.prefixEditDistance("freiburg", "stuttgart", 2));
  }

  /**
   * Tests for the method findMatches().
   */
  @Test
  public void testFindMatches() {
    QGramIndex qgi = new QGramIndex(3, false);
    qgi.buildFromFile("example.tsv");
    assertEquals("([Entity(name='frei', score=3, desc='a word', ped=0)], 1)",
        qgi.findMatches("frei", 0).toString());
    assertEquals(
        "([Entity(name='frei', score=3, desc='a word', ped=0), "
            + "Entity(name='brei', score=2, desc='another word', ped=1)], 2)",
        qgi.findMatches("frei", 2).toString());
    assertEquals("([Entity(name='frei', score=3, desc='a word', ped=2)], 2)",
        qgi.findMatches("freibu", 2).toString());
  }

  /**
   * Tests for the method findMatches().
   */
  @Test
  public void testRankMatches() {
    List<Entity> matches = new ArrayList<>();

    Entity entity1 = new Entity("foo", 3);
    entity1.ped = 2;
    matches.add(entity1);

    Entity entity2 = new Entity("bar", 7);
    entity2.ped = 0;
    matches.add(entity2);

    Entity entity3 = new Entity("baz", 2);
    entity3.ped = 1;
    matches.add(entity3);

    Entity entity4 = new Entity("boo", 5);
    entity4.ped = 1;
    matches.add(entity4);

    assertEquals(
        "[Entity(name='bar', score=7, ped=0), "
            + "Entity(name='boo', score=5, ped=1), "
            + "Entity(name='baz', score=2, ped=1), "
            + "Entity(name='foo', score=3, ped=2)]",
        QGramIndex.rankMatches(matches).toString());
  }

  /**
   * Tests for the method computeQGrams().
   */
  @Test
  public void testComputeQGrams() {
    QGramIndex qgi = new QGramIndex(3, false);
    assertEquals("[$$f, $fr, fre, rei, eib, ibu, bur, urg]",
        qgi.computeQGrams("freiburg").toString());
  }

  /**
   * Tests for the method normalize().
   */
  @Test
  public void testNormalize() {
    assertEquals("freiburg", QGramIndex.normalize("Frei, burg !!"));
    assertEquals("freiburg", QGramIndex.normalize("freiburg"));
  }

  /**
   * Tests for the method SearchServerMain.urlDecode().
   */
  @Test
  public void urlDecode() throws UnsupportedEncodingException {
    assertEquals("nirwana", SearchServerMain.urlDecode("nirwana"));
    assertEquals("the mätrix", SearchServerMain.urlDecode("the+m%C3%A4trix"));
    assertEquals("Mikrösoft Windos",
        SearchServerMain.urlDecode("Mikr%C3%B6soft+Windos"));
    assertEquals("The hitschheiker guide",
        SearchServerMain.urlDecode("The+hitschheiker%20guide"));
  }
}
