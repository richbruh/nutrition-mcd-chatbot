import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "McDonald's Nutrition Assistant | AI-Powered",
  description: "Dapatkan informasi nutrisi menu McDonald's dengan teknologi AI",
  keywords: ["McDonald's", "nutrition", "AI", "chatbot", "kalori", "gizi"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="id" className={inter.variable}>
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}