using AutoListGoogleMeet.Forms;
using CsvHelper;
using CsvHelper.Configuration;
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text;
using System.Text.RegularExpressions;

namespace AutoListGoogleMeet.Models
{
    internal class GoogleMeetCsvParser
    {
        private const int METADATA_LINES_COUNT = 10;

        public GoogleMeetCsvData Parse(string filePath)
        {
            var lines = File.ReadAllLines(filePath);

            MeetCode meetCode = ExtractMeetCode(lines);
            DateTime? meetingDate = ExtractMeetingDate(lines);

            int headerIndex = -1;

            for (int i = 0; i < lines.Length; i++)
            {
                if (lines[i].Contains("Full Name"))
                {
                    headerIndex = i;
                    break;
                }
            }

            if (headerIndex == -1)
            {
                throw new InvalidDataException(
                    "У файлі не знайдено колонку 'Full Name'.");
            }

            var cleanString = string.Join(
                Environment.NewLine,
                lines.Skip(headerIndex));

            var config = new CsvConfiguration(CultureInfo.InvariantCulture)
            {
                Delimiter = ",",
                HasHeaderRecord = true,
                MissingFieldFound = null,
                BadDataFound = null
            };

            var students = new List<string>();

            using (var reader = new StringReader(cleanString))
            using (var csv = new CsvReader(reader, config))
            {
                var records = csv.GetRecords<GoogleMeetRecord>();

                foreach (var record in records)
                {
                    if (!string.IsNullOrEmpty(record.FullName))
                    {
                        students.Add(record.FullName);
                    }
                }
            }

            return new GoogleMeetCsvData
            {
                MeetCode = meetCode,
                MeetingDate = meetingDate,
                Students = students
            };
        }

        private MeetCode ExtractMeetCode(string[] lines)
        {
            string meetCodePattern = @"[a-z]{3}-[a-z]{4}-[a-z]{3}";

            foreach (var line in lines.Take(METADATA_LINES_COUNT))
            {
                Match match = Regex.Match(line, meetCodePattern);

                if (match.Success &&
                    MeetCode.TryParse(match.Value, out MeetCode parsedMeetCode))
                {
                    return parsedMeetCode;
                }
            }

            return null;
        }

        private DateTime? ExtractMeetingDate(string[] lines)
        {
            string combined = string.Join(
                " ",
                lines.Take(METADATA_LINES_COUNT));

            string[] patterns =
            {
                @"\b\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\b",
                @"\b\d{4}[./-]\d{1,2}[./-]\d{1,2}\b",
                @"\b\d{1,2}\s+[A-Za-zА-Яа-я]+\s+\d{4}\b"
            };

            foreach (var pattern in patterns)
            {
                Match match = Regex.Match(combined, pattern);

                if (match.Success)
                {
                    string value = match.Value.Trim().Trim('"', '\'');

                    if (DateTime.TryParse(value, out DateTime date))
                    {
                        return date;
                    }

                    return null;
                }
            }

            return null;
        }
    }
}
