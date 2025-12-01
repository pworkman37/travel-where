import java.awt.*;
import java.io.*;
import java.net.*;
import javax.swing.*;

public class APIcall extends JFrame {
    private static final String API_KEY = "HOVGmCpH1aiyeCiP4os6GexwellBybIZ";
    private static final String API_SECRET = "o0RPAq66ppyX3IDa";

    private JTextField originField;
    private JTextField destField;
    private JTextField dateField;
    private JTextArea outputArea;

    public APIcall() {
        setTitle("Flight Search (Amadeus API)");
        setSize(650, 500);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);

        // Main layout container
        JPanel panel = new JPanel();
        panel.setLayout(new GridBagLayout());
        panel.setBorder(BorderFactory.createEmptyBorder(20, 20, 20, 20));
        GridBagConstraints c = new GridBagConstraints();
        c.insets = new Insets(10, 10, 10, 10);
        c.fill = GridBagConstraints.HORIZONTAL;

        // Origin
        c.gridx = 0; c.gridy = 0;
        panel.add(new JLabel("Origin (e.g., JFK):"), c);

        originField = new JTextField();
        c.gridx = 1; c.gridy = 0;
        panel.add(originField, c);

        // Destination
        c.gridx = 0; c.gridy = 1;
        panel.add(new JLabel("Destination (e.g., ATL):"), c);

        destField = new JTextField();
        c.gridx = 1; c.gridy = 1;
        panel.add(destField, c);

        // Date
        c.gridx = 0; c.gridy = 2;
        panel.add(new JLabel("Departure Date (YYYY-MM-DD):"), c);

        dateField = new JTextField();
        c.gridx = 1; c.gridy = 2;
        panel.add(dateField, c);

        // Search button
        JButton searchButton = new JButton("Search Flights");
        searchButton.setFont(new Font("Arial", Font.BOLD, 14));
        c.gridx = 0; c.gridy = 3; c.gridwidth = 2;
        panel.add(searchButton, c);

        // Output area (scrollable)
        outputArea = new JTextArea();
        outputArea.setEditable(false);
        outputArea.setFont(new Font("Consolas", Font.PLAIN, 13));

        JScrollPane scroll = new JScrollPane(outputArea);
        scroll.setVerticalScrollBarPolicy(ScrollPaneConstants.VERTICAL_SCROLLBAR_ALWAYS);

        // Layout stacking
        setLayout(new BorderLayout());
        add(panel, BorderLayout.NORTH);
        add(scroll, BorderLayout.CENTER);

        // Button logic
        searchButton.addActionListener(e -> searchFlights());
    }

    // Performs the search
    private void searchFlights() {
        String origin = originField.getText().trim();
        String dest = destField.getText().trim();
        String date = dateField.getText().trim();

        outputArea.setText("Searching flights...\n");

        new Thread(() -> {
            String result = searchFlightsAPI(origin, dest, date);
            outputArea.setText(result);
        }).start();
    }

    // Get access token
    private static String getAccessToken() {
        try {
            URL url = new URL("https://test.api.amadeus.com/v1/security/oauth2/token");
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("POST");
            conn.setDoOutput(true);
            conn.setRequestProperty("Content-Type", "application/x-www-form-urlencoded");

            String body = "grant_type=client_credentials"
                    + "&client_id=" + API_KEY
                    + "&client_secret=" + API_SECRET;

            OutputStream os = conn.getOutputStream();
            os.write(body.getBytes());
            os.flush();
            os.close();

            if (conn.getResponseCode() != 200) {
                return "Error: Could not get token (HTTP " + conn.getResponseCode() + ")";
            }

            BufferedReader in = new BufferedReader(new InputStreamReader(conn.getInputStream()));
            StringBuilder sb = new StringBuilder();
            String line;
            while ((line = in.readLine()) != null) sb.append(line);
            in.close();

            String json = sb.toString();

            String find = "\"access_token\":\"";
            int start = json.indexOf(find) + find.length();
            int end = json.indexOf("\"", start);

            return json.substring(start, end);

        } catch (Exception e) {
            return "Error: " + e.getMessage();
        }
    }

    // Flight search call
    private static String searchFlightsAPI(String origin, String destination, String date) {
        try {
            String token = getAccessToken();
            if (token.startsWith("Error")) return token;

            String urlStr =
                "https://test.api.amadeus.com/v2/shopping/flight-offers?"
                + "originLocationCode=" + origin
                + "&destinationLocationCode=" + destination
                + "&departureDate=" + date
                + "&adults=1";

            URL url = new URL(urlStr);
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("GET");
            conn.setRequestProperty("Authorization", "Bearer " + token);

            if (conn.getResponseCode() != 200) {
                return "Error: Search failed (HTTP " + conn.getResponseCode() + ")";
            }

            BufferedReader in = new BufferedReader(new InputStreamReader(conn.getInputStream()));
            StringBuilder sb = new StringBuilder();
            String line;
            while ((line = in.readLine()) != null) sb.append(line).append("\n");
            in.close();

            return sb.toString();

        } catch (Exception e) {
            return "Error: " + e.getMessage();
        }
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new APIcall().setVisible(true));
    }
}
