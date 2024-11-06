import { useAtomValue } from "jotai";
import { Outlet } from "react-router-dom";
import Footer from "../components/Footer";
import { backgroundState } from "../hooks/useBackground";

const Layout = () => {
  const expand = useAtomValue(backgroundState);
  return (
    <div className="relative w-full bg-gray-900 min-h-screen flex flex-col overflow-hidden">
      <Outlet />
      <Footer />

      <div
        className="absolute transition-all duration-[2000ms] max-w-lg blur-[118px] h-[800px] mx-auto sm:max-w-3xl sm:h-[400px]"
        style={{
          transform: expand ? "rotate(-45deg)" : "rotate(45deg)",
          inset: expand ? "0" : "-350px 0px 0px -500px",
          background:
            "linear-gradient(106.89deg, rgba(192, 132, 252, 0.11) 15.73%, rgba(14, 165, 233, 0.41) 15.74%, rgba(232, 121, 249, 0.26) 56.49%, rgba(79, 70, 229, 0.4) 115.91%)",
        }}
      ></div>
      <div
        className="absolute transition-all duration-[2000ms]   max-w-lg blur-[118px] h-[800px] mx-auto sm:max-w-3xl sm:h-[400px]"
        style={{
          transform: expand ? "rotate(45deg)" : "rotate(-45deg)",
          inset: expand ? "0" : "350px 0px 0px 500px",

          background:
            "linear-gradient(106.89deg, rgba(192, 132, 252, 0.11) 15.73%, rgba(14, 165, 233, 0.41) 15.74%, rgba(232, 121, 249, 0.26) 56.49%, rgba(79, 70, 229, 0.4) 115.91%)",
        }}
      ></div>
    </div>
  );
};

export default Layout;
