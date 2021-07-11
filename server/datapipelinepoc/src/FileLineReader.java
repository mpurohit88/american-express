import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.Iterator;

public class FileLineReader implements Iterable<String> {
  private final File inputFile;

  FileLineReader(File inputFile) {
    this.inputFile = inputFile;
  }

  @Override
  public Iterator<String> iterator() {

    try {
      FileInputStream fileInputStream = new FileInputStream(inputFile);
      BufferedReader br = new BufferedReader(new InputStreamReader(fileInputStream, StandardCharsets.UTF_8.name()));

      return new Iterator<String>() {

        @Override
        public boolean hasNext() {
          try {
            return br.ready();
          } catch (IOException e) {
            throw new RuntimeException(e.getMessage(), e);
          }
        }

        @Override
        public String next() {
          try {
            return br.readLine();
          } catch (IOException e) {
            throw new RuntimeException(e.getMessage(), e);
          }
        }
      };

    } catch (Exception e) {
      // something went wrong opening the buffer
      throw new RuntimeException(e.getMessage(), e);
    }
  }
}
