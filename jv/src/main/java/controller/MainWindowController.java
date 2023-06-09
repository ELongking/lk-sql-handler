package controller;

import javafx.event.EventHandler;
import javafx.scene.control.Alert;
import javafx.stage.WindowEvent;
import lombok.SneakyThrows;
import mapper.GeneralMapper;
import model.SqlHandler;
import utils.SqlEditor;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;

import javafx.fxml.FXMLLoader;
import javafx.scene.control.ComboBox;
import javafx.scene.control.TextField;
import javafx.stage.Stage;
import javafx.scene.Scene;

import java.io.IOException;
import java.sql.SQLException;
import java.util.List;


public class MainWindowController {
    private final Stage thisStage;
    private final SqlHandler sqlHandler = new SqlHandler();

    @FXML
    private TextField url_text;
    @FXML
    private TextField username_text;
    @FXML
    private TextField pwd_text;
    @FXML
    private TextField port_text;
    @FXML
    private ComboBox<String> database_box;
    @FXML
    private ComboBox<String> table_box;

    public MainWindowController() {
        thisStage = new Stage();
        thisStage.setOnCloseRequest(new EventHandler<WindowEvent>() {
            @SneakyThrows
            @Override
            public void handle(WindowEvent event) {
                sqlHandler.close();
            }
        });

        try {
            FXMLLoader loader = new FXMLLoader();
            loader.setLocation(getClass().getResource("/MainWindow.fxml"));
            loader.setController(this);
            thisStage.setScene(new Scene(loader.load()));
            thisStage.setTitle("lk-sql-handler; Java Version");
        } catch (IOException e) {
            e.printStackTrace();
        }

        database_box.setDisable(true);
        table_box.setDisable(true);
    }

    public void showStage() {
        thisStage.showAndWait();
    }

    public void loginClick(ActionEvent e) throws Exception {
        String url = url_text.getText();
        String port = port_text.getText();
        url = SqlEditor.urlEditor(url, port);
        String username = username_text.getText();
        String password = pwd_text.getText();

        sqlHandler.setUrl(url);
        sqlHandler.setUsername(username);
        sqlHandler.setPassword(password);
        try{
            sqlHandler.initConn();
        } catch (Exception ex){
            Alert alert = new Alert(Alert.AlertType.ERROR);
            alert.setTitle("ERROR");
            alert.setContentText("连接失败");
            alert.show();
            return;
        }


        List<String> dbs = GeneralMapper.getAllDbs(sqlHandler);
        database_box.getItems().addAll(dbs);
        database_box.getSelectionModel().selectedItemProperty().addListener((observable, oldValue, newValue) -> {
            table_box.getItems().clear();
            List<String> tbs = null;
            try {
                tbs = GeneralMapper.getAllTbs(sqlHandler, newValue);
            } catch (SQLException ex) {
                throw new RuntimeException(ex);
            }
            table_box.getItems().addAll(tbs);
        });

        database_box.setDisable(false);
        table_box.setDisable(false);
    }

    public void resetClick(ActionEvent e) {
        url_text.clear();
        port_text.clear();
        username_text.clear();
        pwd_text.clear();

        table_box.getItems().clear();
        database_box.getItems().clear();

        database_box.setDisable(true);
        table_box.setDisable(true);
    }


    public void openModify() throws Exception {
        String database = database_box.getValue();
        String table = table_box.getValue();

        if (database != null && table != null) {
            ModifyWindowController modifyWindowController = new ModifyWindowController(this, sqlHandler, database, table);
            modifyWindowController.showStage();
        }
        else{
            Alert alert = new Alert(Alert.AlertType.ERROR);
            alert.setTitle("ERROR");
            alert.setContentText("未选择合适的数据库名和表名");
            alert.show();
        }


    }


}
