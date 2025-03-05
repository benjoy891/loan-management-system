const express = require('express');
const dotenv = require('dotenv');
const nodemailer = require('nodemailer');
const bodyParser = require('body-parser');

dotenv.config(); 

const app = express();
app.use(bodyParser.json());

const transporter = nodemailer.createTransport({
    host: process.env.SMTP_HOST,
    port: Number(process.env.SMTP_PORT),
    secure: process.env.SMTP_SECURE === "true",
    auth: {
        user: process.env.SMTP_USER,
        pass: process.env.SMTP_PASS,
    },
});

// Send OTP Email
app.post('/send-otp', async (req, res) => {
    const { email, otp } = req.body;

    const mailOptions = {
        from: process.env.SMTP_USER,
        to: email,
        subject: 'Your OTP Code',
        text: `Your OTP code is: ${otp}`
    };

    try {
        await transporter.sendMail(mailOptions);
        console.log("✅ Email sent successfully!");
        res.status(200).json({ success: true, message: 'OTP sent successfully!' });
    } catch (error) {
        console.error('Error sending email:', error);
        res.status(500).json({ success: false, message: 'Failed to send OTP' });
    }
});

// Start Server
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`🚀 Email service running on port ${PORT}`));
