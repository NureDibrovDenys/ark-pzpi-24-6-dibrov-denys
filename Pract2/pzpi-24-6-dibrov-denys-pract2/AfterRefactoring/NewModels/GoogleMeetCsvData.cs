using System;
using System.Collections.Generic;
using System.Text;

namespace AutoListGoogleMeet.Models
{
    internal class GoogleMeetCsvData
    {
        public MeetCode MeetCode { get; set; }

        public DateTime? MeetingDate { get; set; }

        public List<string> Students { get; set; } = new List<string>();
    }
}
