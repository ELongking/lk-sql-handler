package widgets;

import javafx.scene.control.cell.ComboBoxTableCell;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.EqualsAndHashCode;
import model.SqlHandler;

@EqualsAndHashCode(callSuper = true)
@Data
@AllArgsConstructor
public class ItemCombo extends ComboBoxTableCell<String, String> {
    private int row;
    private int col;
    private SqlHandler sqlHandler;


    @Override
    public void updateItem(String item, boolean empty) {
        super.updateItem(item, empty);
        if (!empty){
            int rowIndex = getIndex();
            int colIndex = getTableView().getColumns().indexOf(getTableColumn());
        }
        comboBoxEditableProperty().addListener((observable, oldValue, newValue) -> {
            String res = newValue.toString();

        });
    }

    private void updateItemHandler(String newData){

    }
}
