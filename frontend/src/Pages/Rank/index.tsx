import { LeftCircleFilled, PieChartOutlined } from "@ant-design/icons";
import { Menu } from "antd";
import { ReactNode, useState } from "react";

import { motion } from "framer-motion";

const Title = ({ children }: { children: ReactNode }) => (
  <motion.div
    initial={{
      "--bg-height": "50%",
    }}
    animate={{
      "--bg-height": "10%",
    }}
    transition={{ type: "spring", duration: 5 }}
    className="inline-block z-10  after:-z-10 bg-transparent relative text-5xl text-white/80 backdrop-blur font-semibold  after:content-['']  after:bg-gradient-to-r after:from-[#1e3a8a] after:to-indigo-500 after:absolute after:w-full after:h-[var(--bg-height)] after:bottom-0 after:left-0 after:right-0"
  >
    {children}
  </motion.div>
);

const Rank = () => {
  // const params = useParams();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <main className="relative flex flex-row flex-1 w-full text-white ">
      <aside
        style={{
          width: collapsed ? 80 : 256,
        }}
        className="!bg-[#001529] shadow-sm transition-all overflow-y-auto overflow-x-hidden  max-h-full relative border-r  border-[#1f2937]"
      >
        {!collapsed && (
          <p className="py-5 mb-2 px-4 font-semibold border-[#1f2937] border-b">
            Github Rank
          </p>
        )}
        <Menu
          defaultSelectedKeys={["1"]}
          mode="inline"
          theme="dark"
          inlineCollapsed={collapsed}
          className="px-2 m-0"
          items={[{ key: "1", icon: <PieChartOutlined />, label: "系统分析" }]}
        />
      </aside>

      <div
        style={{
          left: collapsed ? 72 : 248,
        }}
        className="absolute z-50 top-1/2 cursor-pointer transition-all"
        onClick={() => setCollapsed((c) => !c)}
      >
        <LeftCircleFilled
          style={
            collapsed
              ? {
                  transform: "rotate(180deg)",
                }
              : {}
          }
          className=" transition-all"
        />
      </div>

      <div className="p-6 flex flex-col">
        <Title>系统分析</Title>
      </div>
    </main>
  );
};

export default Rank;
