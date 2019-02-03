
// Copyright 2017 University of Freiburg
// Christian Breu <Breuch@web.de>
// Michael Zinner <zinnermichael@live.com>

import java.io.BufferedReader;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.AbstractMap.SimpleEntry;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * Class for evaluating the InvertedIndex class against a benchmark.
 */
public class EvaluateInvertedIndex {

  /**
   * Reads a benchmark from the given file, separates the different queries and
   * their respective relevant ids, saves them in a Hashmap and then returns the
   * Hashmap.
   * 
   * @param fileName
   *          Filename of the benchmark file that should be read
   * 
   */
  public Map<String, Set<Integer>> readBenchmark(String fileName) {
    Map<String, Set<Integer>> benchMark = new HashMap<>();
    Set<Integer> numbers = new HashSet<Integer>();
    try (BufferedReader reader = Files.newBufferedReader(Paths.get(fileName))) {

      String line;
      while ((line = reader.readLine()) != null) {
        String[] everyThing = line.split("\t");
        String[] nums = everyThing[1].split(" ");
        int i = nums.length;

        // read in all numbers
        for (int k = 0; k < i; k++) {
          numbers.add(Integer.parseInt(nums[k]));
        }
        benchMark.put(everyThing[0], numbers);
        numbers = new HashSet<Integer>();
      }
    } catch (IOException e) {
      System.err.println("An error occured on reading the file:");
      e.printStackTrace();
    }
    return benchMark;
  }

  /**
   * Evaluates the given inverted index against the given benchmark. Processes
   * each query in the benchmark with the given inverted index and compares the
   * result list with the groundtruth in the benchmark. For each query, compute
   * the measures P@3, P@R and AP. Aggregates the values to the three mean
   * measures MP@3, MP@R and MAP and return them.
   * 
   * @param ii
   *          The inverted index that should be evaluated
   * @param benchmark
   *          The benchmark for the given inverted index
   * @param useRefinements
   *          Enables or disables additional refinements. Not currently used.
   * 
   */
  public Triple evaluate(InvertedIndex ii, Map<String, Set<Integer>> benchmark,
      boolean useRefinements) {
    // accumulations of the precisions
    float pat3 = 0;
    float patR = 0;
    float pa = 0;
    for (String query : benchmark.keySet()) {
      // get the relevant List
      Set<Integer> relevantIds = benchmark.get(query);
      // get The invertedList after the query was processed
      List<SimpleEntry<Integer, Double>> resultListRaw = ii
          .process_query(query);
      // convert the List to Integer Type
      List<Integer> resultList = new ArrayList<Integer>();
      for (int i = 0; i < resultListRaw.size(); i++) {
        resultList.add(resultListRaw.get(i).getKey());
      }

      // now calculate the Precisions
      pat3 += precisionAtK(resultList, relevantIds, 3);
      patR += precisionAtK(resultList, relevantIds, relevantIds.size());
      pa += averagePrecision(resultList, relevantIds);
    }
    pat3 /= benchmark.keySet().size();
    patR /= benchmark.keySet().size();
    pa /= benchmark.keySet().size();
    return new Triple(pat3, patR, pa);
  }

  /**
   * Computes the measure P@k for the given list of result ids as it was
   * returned by the inverted index for a single query, and the given set of
   * relevant document ids. Then returns the P@k.
   * 
   * @param resultIds
   *          List of the actual outcome for a given query
   * @param relevantIds
   *          List of relevant results for a given query
   * @param k
   *          Number of elements in result_ids that get compared to relevent_ids
   * 
   */
  public float precisionAtK(List<Integer> resultIds, Set<Integer> relevantIds,
      int k) {
    float matches = 0;
    int counter = k;
    if (resultIds.size() < k) {
      counter = resultIds.size();
    }
    // Check for matches in the first k elements of resultId
    for (int i = 0; i < counter; i++) {
      if (relevantIds.contains(resultIds.get(i))) {
        matches++;
      }
    }
    return (matches / k);
  }

  /**
   * Computes the average precision (AP) for the given list of result ids as it
   * was returned by the inverted index for a single query, and the given set of
   * relevant document ids. Then returns the AP.
   * 
   * @param resultIds
   *          List of the actual outcome for a given query
   * @param relevantIds
   *          List of relevant results for a given query
   * 
   */
  public float averagePrecision(List<Integer> resultIds,
      Set<Integer> relevantIds) {
    float accPre = 0;// accumulated Precisions
    for (int revId : relevantIds) {
      if (resultIds.contains(revId)) {
        accPre += precisionAtK(resultIds, relevantIds,
            resultIds.indexOf(revId) + 1);
      }
    }
    float ap = accPre / relevantIds.size();
    return ap;
  }

}
