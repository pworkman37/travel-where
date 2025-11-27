import javax.swing.*;
import java.awt.*;

public class TravelWhereGUI {

    public TravelWhereGUI() {
        JFrame frame = new JFrame("TravelWhere");
        frame.setSize(500, 450);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setLayout(new GridLayout(8, 1));

        JLabel title = new JLabel("TravelWhere Trip Planner", SwingConstants.CENTER);
        title.setFont(new Font("Arial", Font.BOLD, 20));
        frame.add(title);

        JTextField travelersField = new JTextField();
        JTextField destinationField = new JTextField();
        JTextField dateField = new JTextField();
        JTextField constraintsField = new JTextField();

        frame.add(labeled("Number of Travelers:", travelersField));
        frame.add(labeled("Destination:", destinationField));
        frame.add(labeled("Travel Dates:", dateField));
        frame.add(labeled("Constraints:", constraintsField));

        JButton generateButton = new JButton("Generate Travel Plans");
        frame.add(generateButton);

        JTextArea output = new JTextArea();
        output.setEditable(false);
        frame.add(new JScrollPane(output));

        generateButton.addActionListener(e -> {
            try {
                int travelers = Integer.parseInt(travelersField.getText());
                String dest = destinationField.getText();
                String dates = dateField.getText();
                String constr = constraintsField.getText();

                UserInput input = new UserInput(travelers, dest, dates, new Constraint(constr));
                TravelPlanner planner = new TravelPlanner();
                TravelOption[] options = planner.generateOptions(input);

                output.setText(
                        "=== CHEAP OPTION ===\n" + options[0] +
                        "\n=== BEST VALUE OPTION ===\n" + options[1] +
                        "\n=== PREMIUM OPTION ===\n" + options[2]
                );

            } catch (Exception ex) {
                output.setText("Error: " + ex.getMessage());
            }
        });

        frame.setVisible(true);
    }

    private JPanel labeled(String text, JComponent field) {
        JPanel p = new JPanel(new GridLayout(1, 2));
        p.add(new JLabel(text));
        p.add(field);
        return p;
    }
}

