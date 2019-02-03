
// Copyright 2017 University of Freiburg
// Christian Breu <breuch@web.de>
// Michael Zinner <zinnermichael@live.com>

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.AbstractMap;
import java.util.List;

/**
 * The main class of the inverted index.
 */
public class InvertedIndexMain {
  /**
   * The main method.
   */
  public static void main(String[] args) throws IOException {

    String fileName = "movies.txt";
    InvertedIndex ii = new InvertedIndex();
    ii.readFromFile(fileName, 0.75, 1.75);
    BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
    int i = 0;
    while (i < 1) {
      System.out.print("Enter Keywords: ");
      String snext = br.readLine();
      List<AbstractMap.SimpleEntry<Integer, Double>> outPut = ii
          .process_query(snext);
      if (outPut != null) {
        int count = 0;
        while (outPut.size() >= 1 && count <= 5 && count < outPut.size()) {
          System.out.println(outPut.get(count).toString());
          count++;
        }
      } else {
        System.out.println("no records found");
      }
    }
    br.close();// close the reader

  }
}
