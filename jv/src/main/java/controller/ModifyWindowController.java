package controller;

import javafx.beans.property.SimpleObjectProperty;
import javafx.beans.property.SimpleStringProperty;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.fxml.FXML;
import javafx.scene.control.TableColumn;
import javafx.scene.control.TableView;
import javafx.stage.Stage;
import javafx.fxml.FXMLLoader;
import javafx.scene.Scene;
import mapper.DataMapper;
import mapper.InfoMapper;
import model.SqlHandler;

import java.io.IOException;
import java.util.List;
import java.util.Map;

public class ModifyWindowController {
    private final Stage thisStage;
    private final MainWindowController mainWindowController;
    private final SqlHandler sqlHandler;
    private final String db;
    private final String tb;

    @FXML
    private TableView<Map<String, Object>> data_table;
    @FXML
    private TableView<Map<String, Object>> info_table;

    public ModifyWindowController(MainWindowController mainWindowController, SqlHandler sqlHandler, String db, String tb) {
        this.mainWindowController = mainWindowController;
        this.sqlHandler = sqlHandler;
        this.db = db;
        this.tb = tb;
        thisStage = new Stage();

        try {
            FXMLLoader loader = new FXMLLoader(getClass().getResource("/ModifyWindow.fxml"));
            loader.setController(this);
            thisStage.setScene(new Scene(loader.load()));
            thisStage.setTitle("Now check =>" + db + "." + tb);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public void showStage() throws Exception {
        freshInfo();
        freshData();
        thisStage.showAndWait();
    }

    public void freshInfo() throws Exception {
        info_table.getColumns().clear();
        info_table.getItems().clear();

        List<Map<String, Object>> allInfo = InfoMapper.getAllInfo(sqlHandler, db, tb);
        Map<String, Object> singleInfo = allInfo.get(0);
        for (String key : singleInfo.keySet()) {
            info_table.getColumns().add(new TableColumn<>(key));
        }

        ObservableList<Map<String, Object>> observableAllInfo = FXCollections.observableArrayList(allInfo);
        data_table.setItems(observableAllInfo);
    }

    public void freshData() throws Exception {
        data_table.getColumns().clear();
        data_table.getItems().clear();

        List<Map<String, Object>> allData = DataMapper.getAllData(sqlHandler, db, tb);
        Map<String, Object> singleData = allData.get(0);

        for (Map<String, Object> item : allData) {
            data_table.getItems().add(item);
        }
        for (String key : singleData.keySet()) {
            TableColumn<Map<String, Object>, Object> newCol = new TableColumn<>(key);
            newCol.setCellValueFactory(data -> new SimpleObjectProperty<>(data.getValue().get(key)));
            data_table.getColumns().add(newCol);
        }
    }

}
