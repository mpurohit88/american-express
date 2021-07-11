import java.util.Iterator;

public final class Sink<T> {

  private final Iterator<T> source;
  private final ApplyResult<T> sink;

  Sink(Iterator<T> source, ApplyResult<T> sink) {
    this.source = source;
    this.sink = sink;
  }

  public void execute() {
    while (source.hasNext()) {
      sink.apply(source.next());
    }
  }
}