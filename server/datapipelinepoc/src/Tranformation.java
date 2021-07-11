import java.util.Iterator;

public final class Tranformation<T, D> implements Iterator<D> {

  private final Iterator<T> source;
  private final ApplyFunction<T, D> transformer;

  Tranformation(Iterator<T> source, ApplyFunction<T, D> transformer) {
    this.source = source;
    this.transformer = transformer;
  }

  public <Q> Tranformation<D, Q> transform(ApplyFunction<D, Q> transformer) {
    return new Tranformation<>(this, transformer);
  }

  public Sink<D> sink(ApplyResult<D> result) {
    return new Sink<>(this, result);
  }

  @Override
  public boolean hasNext() {
    return source.hasNext();
  }

  @Override
  public D next() {
    return transformer.apply(source.next());
  }
}