import "@copilotkit/react-ui/styles.css";
import "./globals.css";

import type { Metadata } from "next";
import { IBM_Plex_Sans, IBM_Plex_Serif } from "next/font/google";
import { ReactNode } from "react";

const sans = IBM_Plex_Sans({ subsets: ["latin"], variable: "--font-sans", weight: ["400", "500", "600"] });
const serif = IBM_Plex_Serif({ subsets: ["latin"], variable: "--font-serif", weight: ["400", "600"] });

export const metadata: Metadata = {
  title: "Ontology",
  description: "Ontology project v1",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="zh-CN">
      <body className={`${sans.variable} ${serif.variable}`}>{children}</body>
    </html>
  );
}
