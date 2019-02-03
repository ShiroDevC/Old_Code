import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.Map;
import java.util.Set;

public class EvaluateInvertedIndexMain {

  /**
   * The main method.
   * 
   * @throws IOException
   */
  public static void main(String[] args) throws IOException {
    BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
    InvertedIndex ii = new InvertedIndex();
    EvaluateInvertedIndex ei = new EvaluateInvertedIndex();

    int i = 0;
    while (i < 1) {
      System.out.print("Enter dataset path:");
      String input = br.readLine();
      ii.readFromFile(input, 0.75, 1.75);
      System.out.print("Enter benchmark path:");
      input = br.readLine();
      Map<String, Set<Integer>> benchMark = ei.readBenchmark(input);
      Triple eval = ei.evaluate(ii, benchMark, false);
      System.out.println("MP@3:" + eval.getFirst() + " MP@R:" + eval.getSecond()
          + " MAP:" + eval.getThird());
    }
    br.close();// close the reader
  }

}
