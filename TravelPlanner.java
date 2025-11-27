import java.util.Random;

public class TravelPlanner {

    public TravelOption[] generateOptions(UserInput input) {

        if (input.destination.isEmpty()) {
            throw new IllegalArgumentException("Destination cannot be empty.");
        }

        // Simulated logic
        Random r = new Random();

        TravelOption cheap = new TravelOption(
                "Basic flight + hostel",
                150 + r.nextInt(100),
                "Hostel  shared room",
                input.dates,
                input.travelers
        );

        TravelOption value = new TravelOption(
                "Economy flight + 3-star hotel",
                300 + r.nextInt(150),
                "Hotel  standard room",
                input.dates,
                input.travelers
        );

        TravelOption premium = new TravelOption(
                "First class + resort",
                750 + r.nextInt(300),
                "Luxury resort suite",
                input.dates,
                input.travelers
        );

        return new TravelOption[]{cheap, value, premium};
    }
}
