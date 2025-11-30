import java.awt.*;
import java.text.DecimalFormat;
import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Random;
import javax.swing.*;
import javax.swing.table.*;

public class Hotels extends JFrame {

    private JTextField destinationField;
    private JTextField checkInField;
    private JTextField checkOutField;
    private JTextField guestsField;
    private JTable hotelTable;

    public Hotels() {
        setTitle("Hotel Search Simulator");
        setSize(950, 600);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);

        JPanel inputPanel = new JPanel(new GridBagLayout());
        inputPanel.setBackground(new Color(245, 245, 245));
        inputPanel.setBorder(BorderFactory.createEmptyBorder(20, 20, 20, 20));
        GridBagConstraints c = new GridBagConstraints();
        c.insets = new Insets(10, 10, 10, 10);
        c.fill = GridBagConstraints.HORIZONTAL;

        // Input fields
        c.gridx = 0; c.gridy = 0; inputPanel.add(new JLabel("Destination (City):"), c);
        destinationField = new JTextField(15); c.gridx = 1; inputPanel.add(destinationField, c);

        c.gridx = 0; c.gridy = 1; inputPanel.add(new JLabel("Check-in Date (YYYY-MM-DD):"), c);
        checkInField = new JTextField(15); c.gridx = 1; inputPanel.add(checkInField, c);

        c.gridx = 0; c.gridy = 2; inputPanel.add(new JLabel("Check-out Date (YYYY-MM-DD):"), c);
        checkOutField = new JTextField(15); c.gridx = 1; inputPanel.add(checkOutField, c);

        c.gridx = 0; c.gridy = 3; inputPanel.add(new JLabel("Number of Guests:"), c);
        guestsField = new JTextField("1", 15); c.gridx = 1; inputPanel.add(guestsField, c);

        JButton searchButton = new JButton("Search Hotels");
        searchButton.setFont(new Font("Arial", Font.BOLD, 14));
        searchButton.setBackground(new Color(70, 130, 180));
        searchButton.setForeground(Color.WHITE);
        searchButton.setFocusPainted(false);
        searchButton.setBorder(BorderFactory.createEmptyBorder(10, 20, 10, 20));
        c.gridx = 0; c.gridy = 4; c.gridwidth = 2;
        inputPanel.add(searchButton, c);

        // Table setup
        String[] columns = {"Hotel Name", "Stars", "Room Type", "Guests", "Price per Night", "Nights", "Total Price"};
        DefaultTableModel model = new DefaultTableModel(columns, 0);
        hotelTable = new JTable(model) {
            public boolean getScrollableTracksViewportHeight() {
                return getPreferredSize().height < getParent().getHeight();
            }
        };
        hotelTable.setRowHeight(35);
        hotelTable.setFillsViewportHeight(true);
        hotelTable.setFont(new Font("SansSerif", Font.PLAIN, 14));
        hotelTable.getTableHeader().setFont(new Font("SansSerif", Font.BOLD, 14));
        hotelTable.getTableHeader().setBackground(new Color(100, 149, 237));
        hotelTable.getTableHeader().setForeground(Color.WHITE);

        // Custom cell renderer for colors
        hotelTable.setDefaultRenderer(Object.class, new DefaultTableCellRenderer() {
            DecimalFormat df = new DecimalFormat("#0.00");
            public Component getTableCellRendererComponent(JTable table, Object value, boolean isSelected, boolean hasFocus, int row, int col) {
                Component c = super.getTableCellRendererComponent(table, value, isSelected, hasFocus, row, col);
                c.setBackground(row % 2 == 0 ? Color.WHITE : new Color(240, 240, 240));
                // highlight cheapest hotel
                if (col == 6) { // total price column
                    double price = Double.parseDouble(value.toString().replace("$",""));
                    double minPrice = Double.MAX_VALUE;
                    for (int r=0;r<table.getRowCount();r++) {
                        double p = Double.parseDouble(table.getValueAt(r,6).toString().replace("$",""));
                        if (p<minPrice) minPrice=p;
                    }
                    if (price==minPrice) c.setBackground(new Color(144,238,144)); // light green
                }
                if (isSelected) c.setBackground(new Color(173,216,230));
                return c;
            }
        });

        JScrollPane tableScroll = new JScrollPane(hotelTable);

        setLayout(new BorderLayout());
        add(inputPanel, BorderLayout.NORTH);
        add(tableScroll, BorderLayout.CENTER);

        searchButton.addActionListener(e -> generateHotels(model));
    }

    private void generateHotels(DefaultTableModel model) {
        String destination = destinationField.getText().trim();
        String checkInStr = checkInField.getText().trim();
        String checkOutStr = checkOutField.getText().trim();
        int guests;

        try {
            guests = Integer.parseInt(guestsField.getText().trim());
            if (guests < 1) throw new NumberFormatException();
        } catch (NumberFormatException e) { 
            JOptionPane.showMessageDialog(this,"Enter valid number of guests"); return; 
        }

        if(destination.isEmpty() || checkInStr.isEmpty() || checkOutStr.isEmpty()) {
            JOptionPane.showMessageDialog(this,"Fill all fields"); return;
        }

        LocalDate checkIn, checkOut;
        try {
            checkIn = LocalDate.parse(checkInStr);
            checkOut = LocalDate.parse(checkOutStr);
            if(!checkOut.isAfter(checkIn)) {
                JOptionPane.showMessageDialog(this,"Check-out must be after check-in"); return;
            }
        } catch (Exception e) {
            JOptionPane.showMessageDialog(this,"Invalid date format"); return;
        }

        long nights = ChronoUnit.DAYS.between(checkIn, checkOut);
        model.setRowCount(0);

        List<HotelOffer> offers = generateDummyHotels(destination, guests, nights, 10);
        offers.sort(Comparator.comparingDouble(h -> h.totalPrice));

        DecimalFormat df = new DecimalFormat("#0.00");
        for(HotelOffer h: offers) {
            model.addRow(new Object[]{
                    h.name, h.stars, h.roomType, h.guests,
                    "$"+df.format(h.pricePerNight), nights, "$"+df.format(h.totalPrice)
            });
        }
    }

    private static class HotelOffer {
        String name, roomType;
        int stars, guests;
        double pricePerNight, totalPrice;
    }

    private List<HotelOffer> generateDummyHotels(String destination, int guests, long nights, int count) {
        Random rand = new Random();
        String[] hotelNames = {"Marriott", "Hilton", "Hyatt", "Holiday Inn", "Sheraton", "Best Western"};
        String[] roomTypes = {"Standard", "Deluxe", "Suite", "King", "Queen"};
        List<HotelOffer> hotels = new ArrayList<>();
        for(int i=0;i<count;i++) {
            HotelOffer h = new HotelOffer();
            h.name = hotelNames[rand.nextInt(hotelNames.length)];
            h.stars = 3+rand.nextInt(3); // 3-5 stars
            h.roomType = roomTypes[rand.nextInt(roomTypes.length)];
            h.guests = guests;
            h.pricePerNight = 50 + rand.nextDouble()*250;
            h.totalPrice = h.pricePerNight*nights;
            hotels.add(h);
        }
        return hotels;
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new Hotels().setVisible(true));
    }
}
