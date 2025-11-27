public class Constraint {

    String raw;

    public Constraint(String raw) {
        this.raw = raw;
    }

    public boolean contains(String keyword) {
        return raw.toLowerCase().contains(keyword.toLowerCase());
    }

    @Override
    public String toString() {
        return raw;
    }
}
