public class TravelOption {
    private String description;
    private double cost;
    private String lodging;
    private String dates;
    private int travelers;

    public TravelOption(String description, double cost, String lodging, String dates, int travelers) {
        this.description = description;
        this.cost = cost;
        this.lodging = lodging;
        this.dates = dates;
        this.travelers = travelers;
    }

    @Override
    public String toString() {
        return "Description: " + description +
                "\nEstimated Cost: $" + cost +
                "\nLodging: " + lodging +
                "\nDates: " + dates +
                "\nTravelers: " + travelers +
                "\n------------------------------\n";
    }
}
