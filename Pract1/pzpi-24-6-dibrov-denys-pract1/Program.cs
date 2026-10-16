//до рефакторингу

public class UserService
{
    public decimal ProcessUser(int id, string type, decimal amt)
    {
        if (id > 0)
        {
            if (type == "Admin")
            {
                if (amt > 0)
                {
                    return amt - (amt * 0.2m); 
                }
                else
                {
                    return 0;
                }
            }
            else if (type == "Regular")
            {
                if (amt > 0)
                {
                    return amt - (amt * 0.05m); 
                }
                else
                {
                    return 0;
                }
            }
            else
            {
                return amt;
            }
        }
        return -1;
    }
}


//після рефакторингу

public class UserServiceRefactored
{
    private const decimal AdminDiscountRate = 0.20m;
    private const decimal RegularDiscountRate = 0.05m;

    public decimal CalculateDiscountedAmount(int userId, string userType, decimal amount)
    {
        if (userId <= 0)
            throw new ArgumentException("Invalid user ID.", nameof(userId));

        if (amount <= 0)
            return 0m;

        return userType switch
        {
            "Admin" => ApplyDiscount(amount, AdminDiscountRate),
            "Regular" => ApplyDiscount(amount, RegularDiscountRate),
            _ => amount
        };
    }

    private static decimal ApplyDiscount(decimal amount, decimal discountRate)
    {
        return amount - (amount * discountRate);
    }
}


class Program
{
    static void Main(string[] args)
    {
        var oldUserService = new UserService();
        var newUserService = new UserServiceRefactored();

        var testCases = new[]
        {
            new { Id = 1, Type = "Admin", Amount = 100m },
            new { Id = 2, Type = "Regular", Amount = 200m },
            new { Id = 3, Type = "Guest", Amount = 300m },
            new { Id = -1, Type = "Admin", Amount = 100m },
            new { Id = 4, Type = "Admin", Amount = -50m }
        };

        foreach (var tc in testCases)
        {
            decimal oldResult = oldUserService.ProcessUser(tc.Id, tc.Type, tc.Amount);

            decimal newResult;

            try
            {
                newResult = newUserService.CalculateDiscountedAmount(tc.Id, tc.Type, tc.Amount);
            }
            catch (Exception ex)
            {

                Console.WriteLine($"[ID: {tc.Id}, Type: {tc.Type}, Amt: {tc.Amount}] -> The new code threw an exception: {ex.Message}");
                continue;
            }


            bool isMatch = (oldResult == newResult);//це буде значить, що обидва коди повернули однаковий результат, що є очікуваним
            Console.WriteLine($"Test (ID:{tc.Id}, Type:{tc.Type}, Amt:{tc.Amount}) | Old: {oldResult} | New: {newResult} | Match: {(isMatch ? "OK" : "ERROR")}");
        }
        

    }
}
