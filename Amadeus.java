import java.awt.*;
import java.text.DecimalFormat;
import java.time.LocalTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Random;
import javax.swing.*;
import javax.swing.table.*;


public class Amadeus extends JFrame {

    private JTextField originField;
    private JTextField destField;
    private JTextField dateField;
    private JTextField passengersField;
    private JTable flightTable;

    public Amadeus() {
        setTitle("Flight Search Simulator");
        setSize(1000, 600);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);

        JPanel inputPanel = new JPanel(new GridBagLayout());
        inputPanel.setBackground(new Color(245, 245, 245));
        inputPanel.setBorder(BorderFactory.createEmptyBorder(20, 20, 20, 20));
        GridBagConstraints c = new GridBagConstraints();
        c.insets = new Insets(10, 10, 10, 10);
        c.fill = GridBagConstraints.HORIZONTAL;

        // Input fields
        c.gridx = 0; c.gridy = 0; inputPanel.add(new JLabel("Origin:"), c);
        originField = new JTextField(15); c.gridx = 1; inputPanel.add(originField, c);
        c.gridx = 0; c.gridy = 1; inputPanel.add(new JLabel("Destination:"), c);
        destField = new JTextField(15); c.gridx = 1; inputPanel.add(destField, c);
        c.gridx = 0; c.gridy = 2; inputPanel.add(new JLabel("Departure Date (YYYY-MM-DD):"), c);
        dateField = new JTextField(15); c.gridx = 1; inputPanel.add(dateField, c);
        c.gridx = 0; c.gridy = 3; inputPanel.add(new JLabel("Passengers:"), c);
        passengersField = new JTextField("1", 15); c.gridx = 1; inputPanel.add(passengersField, c);

        JButton searchButton = new JButton("Search Flights");
        searchButton.setFont(new Font("Arial", Font.BOLD, 14));
        searchButton.setBackground(new Color(70, 130, 180));
        searchButton.setForeground(Color.WHITE);
        searchButton.setFocusPainted(false);
        searchButton.setBorder(BorderFactory.createEmptyBorder(10, 20, 10, 20));
        c.gridx = 0; c.gridy = 4; c.gridwidth = 2;
        inputPanel.add(searchButton, c);

        // Table setup
        String[] columns = {"Airline", "Flight #", "Origin", "Destination", "Departure", "Passengers", "Flight Time", "Total Price"};
        DefaultTableModel model = new DefaultTableModel(columns, 0);
        flightTable = new JTable(model) {
            public boolean getScrollableTracksViewportHeight() {
                return getPreferredSize().height < getParent().getHeight();
            }
        };
        flightTable.setRowHeight(35);
        flightTable.setFillsViewportHeight(true);
        flightTable.setFont(new Font("SansSerif", Font.PLAIN, 14));
        flightTable.getTableHeader().setFont(new Font("SansSerif", Font.BOLD, 14));
        flightTable.getTableHeader().setBackground(new Color(100, 149, 237));
        flightTable.getTableHeader().setForeground(Color.WHITE);

        // Custom cell renderer for colors
        flightTable.setDefaultRenderer(Object.class, new DefaultTableCellRenderer() {
            DecimalFormat df = new DecimalFormat("#0.00");
            public Component getTableCellRendererComponent(JTable table, Object value, boolean isSelected, boolean hasFocus, int row, int col) {
                Component c = super.getTableCellRendererComponent(table, value, isSelected, hasFocus, row, col);
                c.setBackground(row % 2 == 0 ? Color.WHITE : new Color(240, 240, 240));
                // highlight cheapest flight
                if (col == 7) { // price column
                    double price = Double.parseDouble(value.toString().replace("$", ""));
                    double minPrice = Double.MAX_VALUE;
                    for (int r = 0; r < table.getRowCount(); r++) {
                        double p = Double.parseDouble(table.getValueAt(r, 7).toString().replace("$", ""));
                        if (p < minPrice) minPrice = p;
                    }
                    if (price == minPrice) c.setBackground(new Color(144, 238, 144)); // light green
                }
                if (isSelected) c.setBackground(new Color(173, 216, 230));
                return c;
            }
        });

        JScrollPane tableScroll = new JScrollPane(flightTable);

        setLayout(new BorderLayout());
        add(inputPanel, BorderLayout.NORTH);
        add(tableScroll, BorderLayout.CENTER);

        searchButton.addActionListener(e -> generateFlights(model));
    }

    private void generateFlights(DefaultTableModel model) {
        String origin = originField.getText().trim().toUpperCase();
        String dest = destField.getText().trim().toUpperCase();
        String date = dateField.getText().trim();
        int passengers;
        try {
            passengers = Integer.parseInt(passengersField.getText().trim());
            if (passengers < 1) throw new NumberFormatException();
        } catch (Exception e) { JOptionPane.showMessageDialog(this,"Invalid passengers"); return; }

        if (origin.isEmpty() || dest.isEmpty() || date.isEmpty()) { JOptionPane.showMessageDialog(this,"Fill all fields"); return; }

        model.setRowCount(0);
        List<FlightOffer> offers = generateDummyFlights(origin, dest, passengers, 10);
        offers.sort(Comparator.comparingDouble(f -> f.price));

        DecimalFormat df = new DecimalFormat("#0.00");
        DateTimeFormatter timeFormat = DateTimeFormatter.ofPattern("HH:mm");

        for (FlightOffer f : offers) {
            model.addRow(new Object[]{
                    f.airline, f.flightNumber, f.origin, f.destination,
                    f.departureTime.format(timeFormat), f.passengers, f.flightTime,
                    "$" + df.format(f.price)
            });
        }
    }

    private static class FlightOffer {
        String airline, flightNumber, origin, destination, flightTime;
        LocalTime departureTime;
        int passengers;
        double price;
    }

    private List<FlightOffer> generateDummyFlights(String origin, String dest, int passengers, int count) {
        Random rand = new Random();
        String[] airlines = {"Delta", "American Airlines", "United", "Southwest", "Alaska Airlines"};
        List<FlightOffer> flights = new ArrayList<>();
        for (int i=0;i<count;i++) {
            FlightOffer f = new FlightOffer();
            f.airline = airlines[rand.nextInt(airlines.length)];
            f.flightNumber = f.airline.substring(0,2).toUpperCase() + (100+rand.nextInt(900));
            f.origin = origin; f.destination = dest;
            f.departureTime = LocalTime.of(rand.nextInt(24), rand.nextInt(60));
            int hours = rand.nextInt(6)+1, minutes=rand.nextInt(60);
            f.flightTime = hours+"h "+minutes+"m";
            double base = 100+rand.nextDouble()*400;
            f.passengers = passengers; f.price = base*passengers;
            flights.add(f);
        }
        return flights;
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new Amadeus().setVisible(true));
    }
}
