import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.junit.Test;

public class EvaluateInvertedIndexTest {

  @Test
  public void testReadBenchmark() {
    Map<String, Set<Integer>> testMap = new HashMap<>();
    Set<Integer> testSet = new HashSet<Integer>();
    testSet.add(3);
    testSet.add(4);
    testMap.put("short film", testSet);
    testSet = new HashSet<Integer>();
    testSet.add(1);
    testSet.add(3);
    testSet.add(4);
    testMap.put("animated film", testSet);
    // Test Case from TIP
    EvaluateInvertedIndex ei = new EvaluateInvertedIndex();
    Map<String, Set<Integer>> benchMark = ei
        .readBenchmark("example-benchmark.txt");
    assertTrue(testMap.equals(benchMark));

  }

  @Test
  public void testprecisionAtK() {
    // Test Case from TIP
    EvaluateInvertedIndex ei = new EvaluateInvertedIndex();
    List<Integer> resultIds = Arrays.asList(5, 3, 6, 1, 2);
    Set<Integer> relevantIds = new HashSet<>(Arrays.asList(1, 2, 5, 6, 7, 8));
    assertEquals(ei.precisionAtK(resultIds, relevantIds, 2), 0.5, 0.01);

  }

  @Test
  public void testAveragePrecision() {
    // Test Case from TIP
    EvaluateInvertedIndex ei = new EvaluateInvertedIndex();
    List<Integer> resultIds = Arrays.asList(7, 17, 9, 42, 5);
    Set<Integer> relevantIds = new HashSet<>(Arrays.asList(5, 7, 12, 42));
    assertEquals(0.525, ei.averagePrecision(resultIds, relevantIds), 0.001);
  }

  @Test
  public void testEvaluate() {
    // Test Case from TIP
    InvertedIndex ii = new InvertedIndex();
    ii.readFromFile("example.txt", 0.75, 1.75);

    EvaluateInvertedIndex ei = new EvaluateInvertedIndex();
    Map<String, Set<Integer>> benchMark = ei
        .readBenchmark("example-benchmark.txt");
    Triple testTriple = ei.evaluate(ii, benchMark, false);
    assertEquals(testTriple.getFirst(), 0.667, 0.001);
    assertEquals(testTriple.getSecond(), 0.833, 0.001);
    assertEquals(testTriple.getThird(), 0.694, 0.001);

  }

}