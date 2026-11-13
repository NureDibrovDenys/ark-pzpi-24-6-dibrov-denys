using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Security.Cryptography.X509Certificates;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using System.Windows.Forms;
//using AutoListGoogleMeet.Models;
using CsvHelper;
using CsvHelper.Configuration;
using Microsoft.VisualBasic.FileIO;
using Microsoft.VisualBasic;
using System.Text.Json;
using AutoListGoogleMeet.Models;

namespace AutoListGoogleMeet.Forms
{
    public partial class Finder : Form
    {
        private List<string> referenceMyStudents;

        private List<string> teachers = new List<string>();

        //private const int METADATA_LINES_COUNT = 10;

        private List<string> loadStudents;

        private GroupData settingsData;


        private MeetCode currentMeetCode = null;

        
        
        
        //private List<string> normalizedMyStudents;

        private List<string> NormalizeStudents(List<string> students)
        {
            if (students == null) return new List<string>();
            return students.Select(s => Regex.Replace(s, @"\s+", " ")).ToList();

        }

        //private string settingsPath = @"D:\PROJECTS AND COURSES\C#\HOME\Automating the Google Meet attendee list\AutoListGoogleMeet\AutoListGoogleMeet\TextFiles\data.json";
        private string settingsPath;


    




        public Finder()
        {
            InitializeComponent();

            // === ДИНАМИЧЕСКИЙ ПУТЬ К НАСТРОЙКАМ ===
            // Получаем папку, откуда запущен .exe
            string baseDir = AppContext.BaseDirectory;
            // Формируем путь к папке TextFiles
            string textFilesFolder = Path.Combine(baseDir, "TextFiles");

            // Если папки TextFiles нет на новом компьютере, создаем её
            if (!Directory.Exists(textFilesFolder))
            {
                Directory.CreateDirectory(textFilesFolder);
            }

            // Формируем итоговый путь к файлу data.json
            settingsPath = Path.Combine(textFilesFolder, "data.json");

            LoadDataFromJson();

            loadStudents = new List<string>();
            //txtReferenceList.Text = string.Join(Environment.NewLine, referenceMyStudents);
            //richTextBox1.Text = string.Join(Environment.NewLine, LoadMyStudentsList());

            if (referenceMyStudents != null)
            {
                txtReferenceList.Text = string.Join(Environment.NewLine, referenceMyStudents);
            }

            // Enable drag-and-drop functionality
            this.AllowDrop = true;
            this.DragEnter += Finder_DragEnter;
            this.DragDrop += Finder_DragDrop;

            PinToolStripMenuItem.Text = "📌";
            PinToolStripMenuItem.AutoSize = true;
            //закрепитьToolStripMenuItem.Click += ЗакрепитьToolStripMenuItem_Click;
            toolTip1.SetToolTip(lblSubject, "Натисніть двічі, щоб змінити назву предмету");

        }


        public void LoadDataFromJson()
        {
            if (!File.Exists(settingsPath))
            {
                MessageBox.Show($"Файл налаштувань не знайдено за адресою \n{settingsPath}\n\n Буде створено новий файл.", "Увага");

                var emptyData = new GroupData();

                referenceMyStudents = new List<string>();
                teachers = new List<string>();
                return;
            }
            try
            {
                string jsonString = File.ReadAllText(settingsPath);
                var groupData = JsonSerializer.Deserialize<GroupData>(jsonString);

                settingsData = JsonSerializer.Deserialize<GroupData>(jsonString);

                referenceMyStudents = groupData?.Students ?? new List<string>();
                teachers = groupData?.Teachers ?? new List<string>();

                if (settingsData != null && settingsData.Subjects == null)
                {
                    settingsData.Subjects = new Dictionary<string, string>();
                }

                txtTeachers.Text = string.Join(Environment.NewLine, teachers);
            }
            catch (Exception ex)
            {

                MessageBox.Show($"Помилка читання файла: {ex.Message}");

                referenceMyStudents = new List<string>();
                teachers = new List<string>();


            }

        }

        private void SaveToDataJson(GroupData groupData)
        {
            var options = new JsonSerializerOptions { WriteIndented = true, Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping };
            string jsonString = JsonSerializer.Serialize(groupData, options);
            File.WriteAllText(settingsPath, jsonString);
        }


        private void Finder_DragEnter(object sender, DragEventArgs e)
        {
            if (e.Data.GetDataPresent(DataFormats.FileDrop))
            {
                e.Effect = DragDropEffects.Copy;
            }
            else
            {
                e.Effect = DragDropEffects.None;
            }
        }

        private void LoadStudentsFromFile(string filePath)
        {
            txtResult.Clear();
            loadStudents.Clear();
            lbNameTeacher.Text = "";

            try
            {
                //передаємо файл парсеру та отримуємо оброблені дані
                var parser = new GoogleMeetCsvParser();
                GoogleMeetCsvData parsedData = parser.Parse(filePath);

                currentMeetCode = parsedData.MeetCode;

                //оновлюємо дату зустрічі
                lblDataMeeting.Text = parsedData.MeetingDate.HasValue
                    ? parsedData.MeetingDate.Value.ToString("dd.MM.yyyy")
                    : "Дата не знайдена";

                //отримуємо список учасників
                loadStudents.AddRange(parsedData.Students);

                foreach (var student in loadStudents)
                {
                    txtResult.AppendText(student + Environment.NewLine);
                }

                //обробляємо предмет, пов'язаний із кодом зустрічі
                if (currentMeetCode != null)
                {
                    if (settingsData == null)
                        settingsData = new GroupData();

                    if (settingsData.Subjects == null)
                        settingsData.Subjects = new Dictionary<string, string>();

                    if (settingsData.Subjects.ContainsKey(currentMeetCode.Value))
                    {
                        lblSubject.Text = "Предмет: " +
                            settingsData.Subjects[currentMeetCode.Value];
                    }
                    else
                    {
                        bool wasPinned = this.TopMost;
                        this.TopMost = false;

                        string subjectName = Interaction.InputBox(
                            $"Знайдено новий код зустрічі: {currentMeetCode.Value}\nВведіть назву предмету.",
                            "Новий предмет",
                            "");

                        this.TopMost = wasPinned;

                        if (!string.IsNullOrWhiteSpace(subjectName))
                        {
                            settingsData.Subjects.Add(
                                currentMeetCode.Value,
                                subjectName);

                            SaveToDataJson(settingsData);
                            lblSubject.Text = "Предмет: " + subjectName;
                        }
                    }
                }

                lblFilesCountable();

                // Визначаємо викладачів серед присутніх учасників
                var presentTeachers = teachers.Where(t =>
                    loadStudents.Any(s =>
                        s.IndexOf(t, StringComparison.OrdinalIgnoreCase) >= 0))
                    .ToList();

                if (presentTeachers.Any())
                {
                    lbNameTeacher.Text =
                        "Викладач(і): " + string.Join("\n", presentTeachers);
                }
            }
            catch (InvalidDataException)
            {
                MessageBox.Show(
                    "Файлі не знайдено колонку 'Full Name'",
                    "Помилка",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error);
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Помилка читання файлу: {ex.Message}");
            }
        }

        private void lblFilesCountable()
        {
            string meetingPath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Desktop), "Meetings");

            if (!Directory.Exists(meetingPath))
            {
                lblFilesCount.Text = "0";
                return;
            }
            int count = Directory.GetFiles(meetingPath, "meeting_*.csv").Length;
            lblFilesCount.Text = $"Залишилось файлів: {count}";
        }


        private void Finder_DragDrop(object sender, DragEventArgs e)
        {
            string[] files = (string[])e.Data.GetData(DataFormats.FileDrop);
            if (files.Length > 0)
            {
                LoadStudentsFromFile(files[0]);
            }
        }


        private void btnLoad_Click(object sender, EventArgs e)
        {

            txtResult.Clear();
            lbNameTeacher.Text = "";
            loadStudents.Clear();


            OpenFileDialog ofd = new OpenFileDialog();
            ofd.Filter = "CSV Files (*.csv)|*.csv|All Files (*.*)|*.*";

            if (ofd.ShowDialog() == DialogResult.OK)
            {
                /* using (TextFieldParser tfp = new TextFieldParser(ofd.FileName))
                 {

                     tfp.TextFieldType = FieldType.Delimited;
                     tfp.HasFieldsEnclosedInQuotes = true;
                     tfp.SetDelimiters(",");

                     bool headerFound = false;

                     string[] header = tfp.ReadFields();

                     while (!tfp.EndOfData)
                     {

                         string[] fields = tfp.ReadFields();



                         if (!headerFound)
                         {
                             if (fields.Length > 0 && fields[0] == "Full Name")
                             {
                                 headerFound = true;
                             }
                             continue;
                         }
                         if (fields.Length > 0)
                         {
                             string fullName = fields[0];
                             loadStudents.Add(fullName);
                             txtResult.AppendText(fullName + Environment.NewLine);
                         }


                     }*/

                LoadStudentsFromFile(ofd.FileName);
                //foreach(var student in students)
                //{
                //    txtResult.AppendText(student + Environment.NewLine);
                //}



            }
        }

        //private void ExtractDataFromCSV(string filePath)
        //{
        //    try
        //    {
        //        //читання перших 10 рядків 
        //        var lines = File.ReadLines(filePath).Take(METADATA_LINES_COUNT);
        //        string combined = string.Join(" ", lines);

        //        //шаблон дат
        //        string[] patterns = new[]
        //        {
        //            @"\b\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\b",   // 31.01.2026, 1/2/26 и т.п.
        //            @"\b\d{4}[./-]\d{1,2}[./-]\d{1,2}\b",     // 2026-01-31
        //            @"\b\d{1,2}\s+[A-Za-zА-Яа-я]+\s+\d{4}\b"  // 31 January 2026 / 31 січня 2026 
        //        };

        //        foreach (var pat in patterns)
        //        {
        //            var match = Regex.Match(combined, pat);
        //            if (match.Success)
        //            {
        //                // убираем кавычки, если есть
        //                var value = match.Value.Trim().Trim('"', '\'');
        //                if (DateTime.TryParse(value, out DateTime date))
        //                {
        //                    lblDataMeeting.Text = date.ToString("dd.MM.yyyy");
        //                }

        //                return;
        //            }
        //        }

        //        // если не нашло — можно поставить подсказку
        //        lblDataMeeting.Text = "Дата не знайдена";
        //    }
        //    catch (Exception ex)
        //    {
        //        MessageBox.Show($"Помилка: {ex.Message}");
        //    }
        //}




        private void btnCompare_Click(object sender, EventArgs e)
        {
            txtAbsentStudents.Clear();

            var normalizedMyStudents = NormalizeStudents(referenceMyStudents);
            var normalizedLoadStudents = NormalizeStudents(loadStudents);
            var absentStudents = normalizedMyStudents.Except(normalizedLoadStudents).ToList();



            foreach (var student in absentStudents)
            {
                txtAbsentStudents.AppendText(student + Environment.NewLine);

            }


        }

        private void label2_Click(object sender, EventArgs e)
        {

        }

        private void label1_Click(object sender, EventArgs e)
        {

        }

        private void txtReferenceList_TextChanged(object sender, EventArgs e)
        {

        }

        private bool isPinned = false;
        private void закрепитьToolStripMenuItem_Click(object sender, EventArgs e)
        {
            isPinned = !isPinned;
            this.TopMost = isPinned;
            PinToolStripMenuItem.Text = isPinned ? "📍" : "📌";
        }

        private bool noFileAlreadyNotify = false;

        private void btnAutoCheck_Click(object sender, EventArgs e)
        {
            string meetingPath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Desktop), "Meetings");
            string archivePath = Path.Combine(meetingPath, "Archive");

            if (!Directory.Exists(meetingPath))
            {
                lblFilesCount.Text = "Папка не знайдена";
                return;
            }
            if (!Directory.Exists(archivePath))
            {
                Directory.CreateDirectory(archivePath);
            }

            var directory = new DirectoryInfo(meetingPath);
            var files = directory.GetFiles("meeting_*.csv").OrderBy(f => f.CreationTime).ToList();

            if (files.Count == 0)
            {
                if (!noFileAlreadyNotify)
                {
                    MessageBox.Show("Файли не знайдені");
                    noFileAlreadyNotify = true;

                }
                return;

            }

            noFileAlreadyNotify = false;

            var nextFile = files[0];

            LoadStudentsFromFile(nextFile.FullName);

            btnCompare_Click(null, null);


            try
            {
                string destFile = Path.Combine(archivePath, nextFile.Name);

                if (File.Exists(destFile))
                {
                    File.Delete(destFile);
                }
                File.Move(nextFile.FullName, destFile);

                lblFilesCountable();
                MessageBox.Show($"Файл успішно оброблено та переміщено в архів: \n{nextFile.FullName}", "Успіх", MessageBoxButtons.OK, MessageBoxIcon.Information);

            }
            catch (Exception ex)
            {
                MessageBox.Show("Не вдалося перемістити файл: " + ex.Message);
            }


        }

        private void btnSaveListStudents_Click(object sender, EventArgs e)
        {



            if (tabControl1.SelectedTab == tabPage1)
            {
                List<string> newStudentsList = txtReferenceList.Lines.Where(lines => !string.IsNullOrEmpty(lines)).Select(lines => lines.Trim()).ToList();
                referenceMyStudents = newStudentsList;
                settingsData.Students = referenceMyStudents;

                MessageBox.Show("Список студентів оновлено!", "Оновлення списка студентів", MessageBoxButtons.OK, MessageBoxIcon.Information);


            }
            else if (tabControl1.SelectedTab == tabPage2)
            {
                List<string> newTeachersList = txtTeachers.Lines.Where(lines => !string.IsNullOrEmpty(lines)).Select(lines => lines.Trim()).ToList();
                teachers = newTeachersList;
                settingsData.Teachers = teachers;
                MessageBox.Show("Список викладачів оновлено!", "Оновлення списка викладачів", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }

            try
            {
                SaveToDataJson(settingsData);

            }
            catch (Exception ex)
            {
                MessageBox.Show($"Помилка при збережені: {ex.Message}", "Помилка", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }

        }

        private void lblSubject_DoubleClick(object sender, EventArgs e)
        {

            if (currentMeetCode == null)
            {
                return;
            }

            string currentName = " ";
            if (settingsData.Subjects.ContainsKey(currentMeetCode.Value))
            {
                currentName = settingsData.Subjects[currentMeetCode.Value];
            }

            bool wasPinned = this.TopMost;
            this.TopMost = false;

            string newName = Interaction.InputBox("Відредагуйте назву предмета: ", "Зміна назви", currentName);

            this.TopMost = wasPinned;

            if (!string.IsNullOrEmpty(newName))
            {
                settingsData.Subjects[currentMeetCode.Value] = newName;
                SaveToDataJson(settingsData);
                lblSubject.Text = "Предмет: " + newName;
            }
        }

        private void toolTip1_Popup(object sender, PopupEventArgs e)
        {

        }

        private void PinToolStripMenuItem_Click(object sender, EventArgs e)
        {
            isPinned = !isPinned;
            this.TopMost = isPinned;
            PinToolStripMenuItem.Text = isPinned ? "📍" : "📌";
        }

        private void lblSubject_Click(object sender, EventArgs e)
        {

        }
    }

    public class GoogleMeetRecord
    {
        [CsvHelper.Configuration.Attributes.Name("Full Name")]
        public string FullName { get; set; }
    }
}
