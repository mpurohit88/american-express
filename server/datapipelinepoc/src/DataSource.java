import java.util.Iterator;

public final class DataSource<T> {

  private Iterator<T> source;

  DataSource(Iterator<T> source) {
    this.source = source;
  }

  public <D> Tranformation<T, D> transform(ApplyFunction<T, D> transformer) {
    return new Tranformation<>(source, transformer);
  }
}