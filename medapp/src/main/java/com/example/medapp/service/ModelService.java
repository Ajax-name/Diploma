package com.example.medapp.service;

import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.file.Files;
import java.util.*;

@Service
public class ModelService {

    private static final String PYTHON_PATH = "/home/alexey/miniconda3/bin/python";
    private static final String DATASET_PATH = "/home/alexey/Рабочий стол/Диплом/medapp/models/dataset";
    private static final String PREDICT_PATH = "/home/alexey/Рабочий стол/Диплом/medapp/models/predict.py";
    private static final String RETRAIN_PATH = "/home/alexey/Рабочий стол/Диплом/medapp/models/retrain.py";

    public String predictModel(List<String> imagePaths) {
        try {
            StringBuilder output = new StringBuilder();

            for (String imagePath : imagePaths) {
                Process process = getPredictProcess(imagePath);

                BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
                StringBuilder temp_output = new StringBuilder();

                String line;

                while ((line = reader.readLine()) != null) {
                    temp_output.append(line).append("\n");
                }

                process.waitFor();

                output.append(resultsDefiner(temp_output.toString(), imagePath)).append(";" + "\u2008" + ";");
            }

            return output.substring(0, output.length() - 2);

        } catch (Exception e) {
            return "Ошибка при запуске модели: " + e.getMessage();
        }
    }

    public void retrainModel(MultipartFile multipartFile, String className) throws IOException, InterruptedException {
        Map<String, String> classes = new HashMap<>(9);
        classes.put("ОКТ Беспигментная гемангиома", "oct_choroidal_hemangioma");
        classes.put("ОКТ Невус хориоидеи", "oct_choroidea_nevus");
        classes.put("ОКТ Меланома", "oct_melanoma");
        classes.put("ОКТ Здоровый глаз", "oct_normal");
        classes.put("Фундус-фото Беспигментная меланома", "photo_amelanotic_melanoma");
        classes.put("Фундус-фото Беспигментная гемангиома", "photo_choroidal_hemangioma");
        classes.put("Фундус-фото Невус хориоидеи", "photo_choroidea_nevus");
        classes.put("Фундус-фото Здоровый глаз", "photo_normal");
        classes.put("Фундус-фото Пигментная меланома", "photo_pigmented_melanoma");

        File trainClassDir = new File(DATASET_PATH + "/train/" + classes.get(className) + "/");
        File valClassDir = new File(DATASET_PATH + "/val/" + classes.get(className) + "/");
        File futureClassDir = new File(DATASET_PATH + "/future/" + classes.get(className) + "/");

        if (!trainClassDir.exists() && !trainClassDir.mkdirs()) {
            throw new IOException("Не удалось создать папку: " + trainClassDir.getAbsolutePath());
        }
        if (!valClassDir.exists() && !valClassDir.mkdirs()) {
            throw new IOException("Не удалось создать папку: " + trainClassDir.getAbsolutePath());
        }
        if (!futureClassDir.exists() && !futureClassDir.mkdirs()) {
            throw new IOException("Не удалось создать папку: " + trainClassDir.getAbsolutePath());
        }

        // Генерируем уникальное имя файла
        String filename = UUID.randomUUID() + ".jpg";
        File trainFile = new File(trainClassDir, filename);
        File valFile = new File(valClassDir, filename);
        File futureFile = new File(futureClassDir, filename);

        multipartFile.transferTo(trainFile);
        Files.copy(trainFile.toPath(), valFile.toPath());
        Files.copy(trainFile.toPath(), futureFile.toPath());

        Process process = getRetrainProcess();
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()))) {
            reader.lines().forEach(System.out::println);
        }

        int exitCode = process.waitFor();
        if (exitCode != 0) {
            throw new RuntimeException("Retrain process failed with exit code " + exitCode);
        }

        // Удаление файлов после обучения
        trainFile.delete();
        valFile.delete();
    }

    private static Process getPredictProcess(String imagePath) throws IOException {
        List<String> command = List.of(PYTHON_PATH, PREDICT_PATH, imagePath);

        ProcessBuilder builder = new ProcessBuilder(command);
        builder.redirectErrorStream(true);

        return builder.start();
    }

    private static Process getRetrainProcess() throws IOException {
        List<String> command = new ArrayList<>();

        command.add(PYTHON_PATH);
        command.add(RETRAIN_PATH);

        ProcessBuilder builder = new ProcessBuilder(command);
        builder.redirectErrorStream(true);

        return builder.start();
    }

    private String resultsDefiner(String output, String imagePath) {
        Map<String, String> classes = new HashMap<>(9);
        classes.put("oct_choroidal_hemangioma", "ОКТ Беспигментная гемангиома");
        classes.put("oct_choroidea_nevus", "ОКТ Невус хориоидеи");
        classes.put("oct_melanoma", "ОКТ Меланома");
        classes.put("oct_normal", "ОКТ Здоровый глаз");
        classes.put("photo_amelanotic_melanoma", "Фундус-фото Беспигментная меланома");
        classes.put("photo_choroidal_hemangioma", "Фундус-фото Беспигментная гемангиома");
        classes.put("photo_choroidea_nevus", "Фундус-фото Невус хориоидеи");
        classes.put("photo_normal", "Фундус-фото Здоровый глаз");
        classes.put("photo_pigmented_melanoma", "Фундус-фото Пигментная меланома");;

        int start = output.lastIndexOf(":") + 2;//imagePath.substring(imagePath.indexOf(".")));
        String[] output_array = output.substring(start).split(" ");

        if (output_array[0].substring(0, 3).contentEquals("oct"))
            output_array[0]= "ОКТ;" + classes.get(output_array[0]);
        else
            output_array[0] = "Фундус-фото;"+ classes.get(output_array[0]);
        String result = String.join(" ", output_array).trim();

        result = result.replace("ОКТ ", "")
                .replace("Фундус-фото ", "");

        return result;
    }

}
