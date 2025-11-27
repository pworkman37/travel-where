public class UserInput {
    int travelers;
    String destination;
    String dates;
    Constraint constraint;

    public UserInput(int travelers, String destination, String dates, Constraint constraint) {
        this.travelers = travelers;
        this.destination = destination;
        this.dates = dates;
        this.constraint = constraint;
    }
}

