
// Copyright 2017 University of Freiburg
// Christian Breu <breuch@web.de>
// Michael Zinner <zinnermichael@live.com>

import java.io.BufferedReader;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.AbstractMap;
import java.util.AbstractMap.SimpleEntry;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * A simple inverted index as explained in lecture 1.
 */
public class InvertedIndex {
  /**
   * The inverted lists.
   */
  protected Map<String, List<AbstractMap.SimpleEntry<Integer,
      Double>>> invertedLists;

  /**
   * Creates an empty inverted index.
   */
  public InvertedIndex() {
    this.invertedLists = new HashMap<>();
  }

  /**
   * Constructs the inverted index from given file (one record per line).
   * 
   * @param file
   *          The path of the file to process.
   */
  public void readFromFile(String file, double b, double k) {
    ArrayList<Integer> wcountList = new ArrayList<Integer>();
    int recordId = 1;
    // first step
    try (BufferedReader reader = Files.newBufferedReader(Paths.get(file))) {

      String line;
      int wordCount = 0;
      while ((line = reader.readLine()) != null) {
        String[] words = line.split("[^A-Za-z]+");
        ArrayList<String> seenList = new ArrayList<String>();
        wordCount = words.length;// get the number of words for each line
        wcountList.add(wordCount);
        for (String word : words) {
          word = word.toLowerCase().trim();

          // Ignore the word if it is empty.
          if (word.isEmpty()) {
            continue;
          }

          SimpleEntry<Integer, Double> entry = new AbstractMap.SimpleEntry<>(
              recordId, 1.0);
          // If word seen first time, create inverted list.
          if (!this.invertedLists.containsKey(word)) {
            this.invertedLists.put(word, new ArrayList<>());
          }

          if (seenList.contains(word)) {
            // If there is an entry for this record already
            int saizu = this.invertedLists.get(word).size() - 1;
            entry = this.invertedLists.get(word).get(saizu);
            double val = entry.getValue();
            this.invertedLists.get(word).get(saizu).setValue(val + 1);
            // increase the count of the record by one
          } else {
            this.invertedLists.get(word).add(entry);
            seenList.add(word);
          }
        }
        recordId++;
      }
    } catch (IOException e) {
      System.err.println("An error occured on reading the file:");
      e.printStackTrace();
    }

    // compute the average document size:
    double avgWordCount = 0;
    for (int c : wcountList) {
      avgWordCount += c;

    }
    recordId--;
    avgWordCount = avgWordCount / wcountList.size();// avg size
    // second step: Iterate over all Inverted Lists and replace the tf values
    for (String word : this.getWords()) {
      List<SimpleEntry<Integer, Double>> list = this.getInvertedList(word);
      int df = list.size();// the df value
      for (SimpleEntry<Integer, Double> entry : list) {
        // get the docLength for the record
        double dl = wcountList.get(entry.getKey() - 1);
        double tf = entry.getValue();
        double val = 0.0;
        // set the bm25 value
        double tfStar = tf * (k + 1)
            / (k * (1 - b + b * dl / avgWordCount) + tf);
        if (k == Double.POSITIVE_INFINITY && b == 0) {
          val = tf// use tf value for standard setting
              * (Math.log(((double) recordId / (double) df)) / Math.log(2));
        } else {
          val = (tfStar// tf* value for normal case
              * (Math.log(((double) recordId / (double) df)) / Math.log(2)));
        }
        // limit the precision of the double values(for tests)
        val *= 1000;
        val = Math.round(val);
        int valInt = (int) val;
        val = (double) valInt / 1000;
        entry.setValue(val);

      }
    }
  }

  /**
   * Returns the words within this inverted index.
   */
  public Set<String> getWords() {
    return this.invertedLists.keySet();
  }

  /**
   * Returns the inverted list for the given word. Returns null if this inverted
   * index doesn't contain an inverted list for the word.
   * 
   * @param word
   *          The word to process.
   */
  public List<SimpleEntry<Integer, Double>> getInvertedList(String word) {
    return this.invertedLists.get(word);
  }

  /**
   * Returns the union of two inverted lists with aggregated bm25 scores
   *
   * @param list1
   *          The first inverted list to process
   * 
   * @param list2
   *          The second inverted list to process
   * 
   */
  public List<SimpleEntry<Integer, Double>> merge(
      List<SimpleEntry<Integer, Double>> list1,
      List<SimpleEntry<Integer, Double>> list2) {
    int i = 0;
    int j = 0;
    List<SimpleEntry<Integer, Double>> list12 = new ArrayList<SimpleEntry
        <Integer, Double>>();
    while (i < list1.size() && j < list2.size()) {
      if (list1.get(i).getKey() == list2.get(j).getKey()) {
        // double precision
        double val = list1.get(i).getValue() + list2.get(j).getValue();
        val *= 1000;
        val = Math.round(val);
        int valInt = (int) val;
        val = (double) valInt / 1000;

        list12.add(new java.util.AbstractMap.SimpleEntry<Integer, Double>(
            list1.get(i).getKey(), val));
        i++;
        j++;
      } else if (list1.get(i).getKey() < list2.get(j).getKey()) {
        list12.add(list1.get(i));
        i++;
      } else {
        list12.add(list2.get(j));
        j++;
      }
    }
    return list12;
  }

  /**
   * Process the given keyword query as follows: Fetch the inverted list for
   * each of the keywords in the query and compute the union of all lists. Sort
   * the resulting list by BM25 scores in descending order.
   * 
   * @param query
   *          The keywords as a singular string that get processed
   * 
   */
  public List<SimpleEntry<Integer, Double>> process_query(String query) {
    String[] words = query.split(" ");
    int length = words.length;
    List<SimpleEntry<Integer, Double>> intersectList = new ArrayList<SimpleEntry
        <Integer, Double>>();
    if (length == 1) {
      intersectList = this.getInvertedList(words[0]);
    } else if (length >= 2) {
      intersectList = this.merge(this.getInvertedList(words[0]),
          this.getInvertedList(words[1]));
      int i = 2;
      while (i < length) {
        intersectList = this.merge(intersectList,
            this.getInvertedList(words[i]));
        i++;
      }
    }

    // Sorting the results
    Collections.sort(intersectList,
        new Comparator<SimpleEntry<Integer, Double>>() {
          @Override
          public int compare(SimpleEntry<Integer, Double> o1,
              SimpleEntry<Integer, Double> o2) {
            return o2.getValue().compareTo(o1.getValue());
          }
        });
    /*List<SimpleEntry<Integer, Double>> returnList = new ArrayList<SimpleEntry
            <Integer, Double>>();
    returnList.add(intersectList.get(0));
    returnList.add(intersectList.get(1));
    returnList.add(intersectList.get(2));
    */
    return intersectList;
  }
}