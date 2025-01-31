"use client";

import { Poppins } from "next/font/google";
import { HeroUIProvider } from "@heroui/react";
import "./globals.css";

const poppinsFont = Poppins({
  subsets: ["latin"],
  weight: "400",
});

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={poppinsFont.className}>
        <HeroUIProvider>{children}</HeroUIProvider>
      </body>
    </html>
  );
}
