import { Input } from "antd";
import { motion, useAnimationControls } from "framer-motion";

import { SearchOutlined } from "@ant-design/icons";
import { useClickAway } from "ahooks";
import { useEffect, useRef, useState } from "react";

const Home = () => {
  const controlLeft = useAnimationControls();
  const controlRight = useAnimationControls();
  const mediumControl = useAnimationControls();
  const ref = useRef<HTMLDivElement | null>(null);

  const [expand, setExpand] = useState(false);

  useClickAway(() => {
    setExpand(false);
  }, ref);

  useEffect(() => {
    if (expand) {
      mediumControl.start({
        height: 300,
      });

      controlLeft.start({
        rotate: -45,
        inset: "0px 0px 0px 0px",
      });

      controlRight.start({
        rotate: 45,
        inset: "0px 0px 0px 0px",
      });
    } else {
      mediumControl.start({
        height: 43,
      });

      controlLeft.start({
        rotate: 45,
        inset: "-350px 0px 0px -500px",
      });

      controlRight.start({
        rotate: -45,
        inset: "350px 0px 0px 500px",
      });
    }
  }, [expand]);

  return (
    <main className="relative py-28 bg-gray-900 min-h-screen w-full overflow-hidden">
      <div className="relative z-10 max-w-screen-xl mx-auto text-gray-600 sm:px-4 md:px-8">
        <div className="max-w-lg space-y-3 px-4 sm:mx-auto sm:text-center sm:px-0">
          <p className="text-white text-3xl font-semibold sm:text-4xl">
            寻找，你的下一个
          </p>
          <p className="text-gray-300">搜索你想要的Github</p>
        </div>
        <motion.div
          ref={ref}
          animate={mediumControl}
          initial={{ height: 43 }}
          transition={{ duration: 2, type: "spring" }}
          className="mt-12 mx-auto   rounded-3xl  bg-white max-w-lg shadow-sm hover:shadow-md "
        >
          <form onSubmit={(e) => e.preventDefault()} className="space-y-5">
            <Input
              bordered={false}
              style={{
                width: "100%",
                height: 43,
                borderBottom: expand ? 1 : 0,
              }}
              onClick={() => {
                setExpand(true);
              }}
              placeholder="Github"
              size="large"
              suffix={
                <SearchOutlined
                  style={{
                    fontSize: 20,
                  }}
                />
              }
            />
          </form>
        </motion.div>
      </div>
      <motion.div
        initial={{ rotate: 45, inset: "-350px 0px 0px -500px" }}
        animate={controlLeft}
        transition={{ duration: 15, type: "spring" }}
        className="absolute max-w-lg blur-[118px] h-[800px] mx-auto sm:max-w-3xl sm:h-[400px]"
        style={{
          background:
            "linear-gradient(106.89deg, rgba(192, 132, 252, 0.11) 15.73%, rgba(14, 165, 233, 0.41) 15.74%, rgba(232, 121, 249, 0.26) 56.49%, rgba(79, 70, 229, 0.4) 115.91%)",
        }}
      ></motion.div>
      <motion.div
        initial={{ rotate: -45, inset: "350px 0px 0px 500px" }}
        animate={controlRight}
        transition={{ duration: 15, type: "spring" }}
        className="absolute  max-w-lg blur-[118px] h-[800px] mx-auto sm:max-w-3xl sm:h-[400px]"
        style={{
          background:
            "linear-gradient(106.89deg, rgba(192, 132, 252, 0.11) 15.73%, rgba(14, 165, 233, 0.41) 15.74%, rgba(232, 121, 249, 0.26) 56.49%, rgba(79, 70, 229, 0.4) 115.91%)",
        }}
      ></motion.div>
    </main>
  );
};

export default Home;
