<?php
use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception;

require __DIR__ . '/vendor/autoload.php';

// Get CLI arguments
$username = $argv[1] ?? 'User';
$email = $argv[2] ?? 'example@example.com';
$password = $argv[3] ?? '******';

$mail = new PHPMailer(true);

try {
    $mail->isSMTP();
    $mail->Host       = 'smtp.gmail.com';
    $mail->SMTPAuth   = true;
    $mail->Username   = 'halderabir2004@gmail.com';
    $mail->Password   = 'eeiaendrkhqfljzd';
    $mail->SMTPSecure = PHPMailer::ENCRYPTION_STARTTLS;
    $mail->Port       = 587;

    $mail->setFrom('halderabir2004@gmail.com', 'RecipeGPT');
    $mail->addAddress($email, $username);

    $mail->isHTML(true);
    $mail->Subject = 'Welcome to RecipeGPT';
    $mail->Body    = "
        <h2>Welcome to RecipeGPT!</h2>
        <p>Your registration details:</p>
        <ul>
            <li>Username: $username</li>
            <li>Email: $email</li>
            <li>Password: $password</li>
            <li>Registration Date: " . date('Y-m-d H:i:s') . "</li>
        </ul>
        <p>Thank you for joining RecipeGPT!</p>
    ";

    $mail->send();
    echo "Mail sent successfully!";
} catch (Exception $e) {
    echo "Mailer Error: {$mail->ErrorInfo}";
}
