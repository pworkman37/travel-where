import javax.swing.*;
import java.awt.*;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.*;

public class Main extends JFrame {

    private JTextField destinationField, travelersField, startDateField, endDateField;
    private JTextArea outputArea;

    public Main() {
        setTitle("TravelWhere");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLayout(new BorderLayout(15, 15));

        // --- Input Panel ---
        JPanel inputPanel = new JPanel();
        inputPanel.setLayout(new GridBagLayout());
        GridBagConstraints gbc = new GridBagConstraints();
        gbc.insets = new Insets(8, 8, 8, 8);
        gbc.fill = GridBagConstraints.HORIZONTAL;

        // Destination
        gbc.gridx = 0; gbc.gridy = 0;
        inputPanel.add(new JLabel("Destination:"), gbc);
        gbc.gridx = 1;
        destinationField = new JTextField(20);
        inputPanel.add(destinationField, gbc);

        // Travelers
        gbc.gridx = 0; gbc.gridy = 1;
        inputPanel.add(new JLabel("Number of Travelers:"), gbc);
        gbc.gridx = 1;
        travelersField = new JTextField(10);
        inputPanel.add(travelersField, gbc);

        // Start Date
        gbc.gridx = 0; gbc.gridy = 2;
        inputPanel.add(new JLabel("Start Date (MM/DD):"), gbc);
        gbc.gridx = 1;
        startDateField = new JTextField(10);
        inputPanel.add(startDateField, gbc);

        // End Date
        gbc.gridx = 0; gbc.gridy = 3;
        inputPanel.add(new JLabel("End Date (MM/DD):"), gbc);
        gbc.gridx = 1;
        endDateField = new JTextField(10);
        inputPanel.add(endDateField, gbc);

        add(inputPanel, BorderLayout.NORTH);

        // --- Output Area ---
        outputArea = new JTextArea();
        outputArea.setEditable(false);
        outputArea.setFont(new Font("Monospaced", Font.PLAIN, 14));
        outputArea.setLineWrap(true);
        outputArea.setWrapStyleWord(true);
        JScrollPane outputScroll = new JScrollPane(outputArea);
        outputScroll.setPreferredSize(new Dimension(700, 350));
        add(outputScroll, BorderLayout.CENTER);

        // --- Generate Button ---
        JButton generateBtn = new JButton("Generate Travel Options");
        generateBtn.setFont(new Font("SansSerif", Font.BOLD, 14));
        generateBtn.setBackground(new Color(59, 89, 182));
        generateBtn.setForeground(Color.WHITE);
        generateBtn.setFocusPainted(false);
        generateBtn.addActionListener(e -> generateTravelOptions());
        JPanel buttonPanel = new JPanel();
        buttonPanel.add(generateBtn);
        add(buttonPanel, BorderLayout.SOUTH);

        pack();
        setLocationRelativeTo(null); // Center on screen
    }

    private void generateTravelOptions() {
        String destination = destinationField.getText().trim();
        String travelersText = travelersField.getText().trim();

        if (destination.isEmpty() || travelersText.isEmpty()) {
            JOptionPane.showMessageDialog(this, "Please enter all required fields!");
            return;
        }

        int travelers;
        try {
            travelers = Integer.parseInt(travelersText);
            if (travelers <= 0) throw new NumberFormatException();
        } catch (Exception e) {
            JOptionPane.showMessageDialog(this, "Travelers must be a positive number.");
            return;
        }

        // Validate dates
        SimpleDateFormat sdf = new SimpleDateFormat("MM/dd");
        sdf.setLenient(false);
        try {
            Date startDate = sdf.parse(startDateField.getText().trim());
            Date endDate = sdf.parse(endDateField.getText().trim());
            if (startDate.after(endDate)) {
                JOptionPane.showMessageDialog(this, "Start date must be before end date!");
                return;
            }
        } catch (ParseException ex) {
            JOptionPane.showMessageDialog(this, "Dates must be in MM/DD format.");
            return;
        }

        // Simulated travel database
        Map<String, Integer> flights = Map.of(
                "Cheap Flight", 150,
                "Best Value Flight", 350,
                "Premium Flight", 800
        );
        Map<String, Integer> hotels = Map.of(
                "Hostel", 40,
                "3-Star Hotel", 120,
                "5-Star Resort", 350
        );

        // Generate 3 plans
        String cheap = generatePlan("Cheap", flights.get("Cheap Flight"), hotels.get("Hostel"), travelers);
        String best = generatePlan("Best Value", flights.get("Best Value Flight"), hotels.get("3-Star Hotel"), travelers);
        String premium = generatePlan("Premium", flights.get("Premium Flight"), hotels.get("5-Star Resort"), travelers);

        outputArea.setText("Travel Options to " + destination + ":\n\n" + cheap + "\n\n" + best + "\n\n" + premium);
    }

    private String generatePlan(String type, int flightCost, int hotelCost, int travelers) {
        int totalFlight = flightCost * travelers;
        int totalHotel = hotelCost * travelers;

        return "=== " + type + " Option ===\n" +
               "Flight: $" + totalFlight + "\n" +
               "Hotel:  $" + totalHotel + "\n" +
               "Total:  $" + (totalFlight + totalHotel) + "\n" +
               "Includes flights + lodging for " + travelers + " traveler(s)";
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new Main().setVisible(true));
    }
}
