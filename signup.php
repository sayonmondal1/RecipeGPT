<?php
// Start session if needed
session_start();

// Include PHPMailer
use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception;
require 'vendor/autoload.php';

// If form submitted
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Collect form data
    $username = $_POST['username'] ?? '';
    $email = $_POST['email'] ?? '';
    $password = $_POST['password'] ?? '';
    $confirmPassword = $_POST['confirmPassword'] ?? '';

    // Simple validation
    if (!$username || !$email || !$password || !$confirmPassword) {
        $error = "Please fill in all fields.";
    } elseif ($password !== $confirmPassword) {
        $error = "Passwords do not match!";
    } else {
        // At this point, you can insert into DB later
        // For now, send confirmation email

        $mail = new PHPMailer(true);
        try {
            // SMTP configuration
            $mail->isSMTP();
            $mail->Host       = 'smtp.technoindiaeducation.com';
            $mail->SMTPAuth   = true;
            $mail->Username   = 'abir221001020057@technoindiaeducation.com'; // your email
            $mail->Password   = 'estv eetv huqe yeot'; // SMTP key
            $mail->SMTPSecure = 'tls'; // or 'ssl'
            $mail->Port       = 587;   // 587 for TLS, 465 for SSL

            // Sender & recipient
            $mail->setFrom('abir221001020057@technoindiaeducation.com', 'RecipeGPT');
            $mail->addAddress($email, $username);

            // Email content
            $mail->isHTML(true);
            $mail->Subject = 'Welcome to RecipeGPT!';
            $mail->Body    = "
                <h2>Hello $username,</h2>
                <p>Your account has been successfully created.</p>
                <p><b>Email:</b> $email<br>
                <b>Password:</b> $password<br>
                <b>Date:</b> ".date('Y-m-d H:i:s')."</p>
                <p>Thank you for joining RecipeGPT!</p>
            ";

            $mail->send();
            $success = "Welcome $username! Confirmation email sent.";
        } catch (Exception $e) {
            $error = "Email could not be sent. Mailer Error: {$mail->ErrorInfo}";
        }
    }
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Signup - RecipeGPT</title>
  <link rel="stylesheet" href="static/css/signup.css">
</head>
<body>
  <header>
    <div class="logo">Recipe<span style="color:yellow;">GPT</span></div>
    <nav>
      <ul>
        <li><a href="index.php">Home</a></li>
        <li><a href="about.php">About</a></li>
        <li><a href="contact.php">Contact</a></li>
        <li><a href="signup.php">Account</a></li>
      </ul>
    </nav>
  </header>

  <section class="signup-section">
    <div class="signup-box">
      <h2>Create an Account</h2>

      <?php if(!empty($error)) echo "<p style='color:red;'>$error</p>"; ?>
      <?php if(!empty($success)) echo "<p style='color:green;'>$success</p>"; ?>

      <form method="POST" id="signupForm">
        <input type="text" name="username" placeholder="Username" required>
        <input type="email" name="email" placeholder="Email" required>
        <input type="password" name="password" placeholder="Password" required>
        <input type="password" name="confirmPassword" placeholder="Confirm Password" required>
        <button type="submit">Sign Up</button>
      </form>

      <p class="login-link">Already have an account? <a href="login.php">Login here</a></p>
    </div>
  </section>
</body>
</html>
