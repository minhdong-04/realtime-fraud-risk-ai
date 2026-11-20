import "@/lib/suppress-hydration";
import "./globals.css";
import { Navbar } from "@/components/Navbar";
import { NotificationProvider } from "@/components/NotificationProvider";
import { AuthProvider } from "@/components/AuthProvider";
import { ClientOnly } from "@/components/ClientOnly";

/**
 * {
 *   func   : RootLayout
 *   desc   : Khung giao dien goc bao boc toan bo he thong, su dung module suppress-hydration va ClientOnly
 *   input  : children (React.ReactNode)
 *   output : JSX.Element
 *   loop   : 0 loops
 * }
 */
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="vi" className="dark" suppressHydrationWarning>
      <head>
        <title>SentinelRisk AI — Real-Time Fraud Detection Platform</title>
        <meta
          name="description"
          content="Nền tảng phát hiện gian lận và đánh giá rủi ro giao dịch thời gian thực với AI giải thích được (SHAP)"
        />
      </head>
      <body
        className="min-h-screen bg-[#080C14] text-white antialiased selection:bg-[#30adcd] selection:text-white relative overflow-x-hidden font-sans"
        suppressHydrationWarning
      >
        <ClientOnly>
          {/* Background Ambient Glow tu ma mau Blue #30adcd & Purple #565ac4 */}
          <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden" suppressHydrationWarning>
            <div className="absolute -top-40 left-1/4 w-96 h-96 bg-[#30adcd]/15 rounded-full blur-3xl" suppressHydrationWarning />
            <div className="absolute top-1/3 -right-20 w-80 h-80 bg-[#565ac4]/15 rounded-full blur-3xl" suppressHydrationWarning />
            <div className="absolute bottom-10 left-10 w-96 h-96 bg-[#2cb285]/10 rounded-full blur-3xl" suppressHydrationWarning />
          </div>

          <AuthProvider>
            <NotificationProvider>
              <div className="relative z-10" suppressHydrationWarning>
                <Navbar />
                <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8" suppressHydrationWarning>
                  {children}
                </main>
              </div>
            </NotificationProvider>
          </AuthProvider>
        </ClientOnly>
      </body>
    </html>
  );
}
