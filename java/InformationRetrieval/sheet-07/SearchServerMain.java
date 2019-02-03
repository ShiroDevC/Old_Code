
// Copyright 2017
// Christian Breu <Breuch@web.de>
// Michael Zinner <zinnermichael@live.com>

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.UnsupportedEncodingException;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.SocketTimeoutException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;

/**
 * Basic server code that returns the contents of a requested file.
 */
public class SearchServerMain {
  /**
   * The main method.
   */
  public static void main(String[] args) throws IOException {
    // Parse the command line arguments.
    if (args.length < 2) {
      System.out.println("java -jar SearchServerMain <port> <entity-file> "
          + "[--with-synonyms]");
      System.exit(1);
    }
    String fileName = args[1];
    boolean withSynonyms = args.length > 1 && args[1].equals("--with-synonyms");

    System.out.print("Building index from '" + fileName + "' ... ");
    System.out.flush();

    // Build a 3-gram index from the given file.
    long start = System.currentTimeMillis();
    QGramIndex index = new QGramIndex(3, withSynonyms);
    index.buildFromFile(fileName);
    long end = System.currentTimeMillis();

    System.out.println("done in " + (end - start) + "ms.");

    int port = Integer.parseInt(args[0]);

    @SuppressWarnings("resource")
    ServerSocket server = new ServerSocket(port);

    // Server loop.
    while (true) {
      // Wait for client.
      System.out.print("Waiting for query on port " + port + " ... ");
      System.out.flush();
      System.out.println(server.getLocalSocketAddress());
      Socket client = server.accept();
      System.out.println("client connected from " + client.getInetAddress());

      // Client connected; set read timeout.
      try {
        client.setSoTimeout(1000);
        // read the whole Request from the client.
        BufferedReader input = new BufferedReader(
            new InputStreamReader(client.getInputStream()));
        StringBuilder request = new StringBuilder();
        while (true) {
          String line = input.readLine();
          // check if the whole Request is sent
          if (line.equals("")) {
            break;
          }
          request.append(line);
        }
        String reqString = request.toString();
        System.out.println(reqString);

        // initialize the content type as plain text.
        String contentType = "text/plain";
        // request status, initially ok
        String reqStatus = "HTTP/1.1 200 OK";
        String contentString = "";
        // initialize empty content
        byte[] contentBytes = contentString.getBytes("UTF-8");
        if (reqString.startsWith("GET")) {
          // extract the actual name of the requested file.
          reqString = reqString.substring(5, reqString.indexOf(" HTTP"));
          String prefix = "";
          String result = "";
          // Read contents of file.
          // check if there is an API Request
          if (reqString.startsWith("api?q=")) {
            // getting String starting from actual request
            prefix = reqString.substring(6);
            prefix = urlDecode(prefix);
            System.out.println(prefix);
            System.out.println();

            // Compute the fuzzy search query
            String query = QGramIndex.normalize(prefix);
            int delta = query.length() / 4;
            start = System.currentTimeMillis();
            ObjectIntPair<List<Entity>> queryResult = index.findMatches(query,
                delta);
            end = System.currentTimeMillis();
            List<Entity> matches = queryResult.first;

            int numResults = Math.min(5, matches.size());
            result = "[ ";
            if (numResults > 0) {
              for (int i = 0; i < numResults; i++) {
                Entity e = matches.get(i);
                result = result + "\"" + e.wikipediaUrl + "^" + e.name + "^"
                    + e.score + "^" + e.desc + "\"";
                // add , to make results an array
                if (i < numResults - 1) {
                  result = result + ", ";
                }
              }
              result = result + " ]";
              result = urlDecode(result);
              if (result.contains("</script>")) {
                System.out.println("Found a script!\n");
                result = result.replaceAll("<script.+</script>", "");
              }
            } else {
              result += "]";
            }
            System.out.println("result: " + result);
            contentString = new String(contentBytes, "UTF-8");
            contentBytes = result.getBytes("UTF-8");
            contentType = "application/json";

          } else {
            // check if the request is only a filename(and no path elsewhere)
            if (!reqString.matches("[a-zA-Z0-9.?=]+")) {
              // access forbidden
              reqStatus = "HTTP/1.1 403 Forbidden";
              // set new contentbytes
              String forbidden = "forbidden";
              contentBytes = forbidden.getBytes("UTF-8");
            } else {
              // Get the file
              Path file = Paths.get(reqString);
              System.out.print("request for" + reqString);
              // check if the file exists and is readable
              if (Files.isRegularFile(file) && Files.isReadable(file)) {
                contentBytes = Files.readAllBytes(file);
                // change the Type of the Response if applicable
                if (reqString.endsWith("html")) {
                  // html
                  contentType = "text/html";
                } else if (reqString.endsWith("css")) {
                  // css
                  contentType = "text/css";
                } else if (reqString.endsWith("js")) {
                  // javascript
                  contentType = "application/javascript";
                }
              } else {
                // no file found, change header accordingly.
                reqStatus = "HTTP/1.1 404 Not found";
              }
            }
          }
        } else {
          // set contentString
          contentString = "No response for non Get requests\n";

        }
        // make the header
        StringBuilder headerB = new StringBuilder();
        headerB.append(reqStatus + "\r\n");// append \r\n for the browser
        headerB.append("Content-Length: " + contentBytes.length + "\r\n");
        headerB.append("Content-Type: " + contentType + "\r\n");
        headerB.append("\r\n");
        // Send the response.
        DataOutputStream output = new DataOutputStream(
            client.getOutputStream());
        output.write(headerB.toString().getBytes("UTF-8"));
        output.write(contentBytes);

        // close everything
        output.close();
        input.close();
        client.close();

      } catch (SocketTimeoutException ste) {
        client.setSoTimeout(1000);// ?
      }
    }
  }

  /**
   * Decodes an q-grams URL-encoded UTF-8 string
   *
   * @param encoded
   *          The URL-encoded string to process.
   *
   * @return The decoded string.
   */
  public static String urlDecode(String encoded)
      throws UnsupportedEncodingException {
    String decoded = java.net.URLDecoder.decode(encoded, "UTF-8");
    return decoded;
  }

}
