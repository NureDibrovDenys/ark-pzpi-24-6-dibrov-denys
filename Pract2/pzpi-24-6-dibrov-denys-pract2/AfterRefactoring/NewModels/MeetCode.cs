using System;
using System.Collections.Generic;
using System.Text;
using System.Text.RegularExpressions;

namespace AutoListGoogleMeet.Models
{
    internal class MeetCode
    {
        public string Value { get; }

        private MeetCode(string value)
        {
            Value = value;
        }

        public static bool TryParse(string value, out MeetCode meetCode)
        {
            meetCode = null;

            if (string.IsNullOrWhiteSpace(value))
            {
                return false;
            }

            if (!Regex.IsMatch(value, @"^[a-z]{3}-[a-z]{4}-[a-z]{3}$"))
            {
                return false;
            }

            meetCode = new MeetCode(value);
            return true;
        }
    }
}
