import java.util.Arrays;
import java.util.HashSet;
import java.util.Iterator;

public class App {

    public static void main(String[] args) {
        Sink<Double> sink = new DataSource<>(Arrays.asList("1", "2", "3", "4").iterator())
                .transform(s -> Integer.parseInt(s)).transform(i -> (double) i)
                .sink(i -> System.out.println("The result is: " + i));

        // prints 1.0, 2.0, 3.0, 4.0
        sink.execute();
    }
}