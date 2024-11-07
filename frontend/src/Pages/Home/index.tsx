import { Input } from "antd";

import { LoadingOutlined, SearchOutlined } from "@ant-design/icons";
import { useClickAway, useRequest } from "ahooks";
import { useSetAtom } from "jotai";
import { useRef, useState } from "react";
import { backgroundState } from "../../hooks/useBackground";
import "./index.css";

const Home = () => {
  const ref = useRef<HTMLDivElement | null>(null);
  const startAnimation = useSetAtom(backgroundState);
  const [hide, setHide] = useState(true);
  const [input, setInput] = useState("");

  useClickAway(() => {
    setHide(true);
    startAnimation(false);
  }, ref);

  const { loading } = useRequest(
    async () => {
      const res = await fetch(`http://api.jellyqwq.top/search?q=${input}`, {
        method: "GET",

        headers: {
          "Content-Type": "application/json",
        },
      });
      console.log(res);
    },
    {
      debounceWait: 500,
      refreshDeps: [input],
    }
  );

  return (
    <main className="relative pt-28  flex-1 w-full overflow-hidden">
      <div className="relative z-10 max-w-screen-xl mx-auto text-gray-600 sm:px-4 md:px-8">
        <div className="max-w-lg space-y-3 px-4 sm:mx-auto sm:text-center sm:px-0">
          <p className="transition-all text-white duration-[2500ms] text-4xl font-semibold ">
            Github Rank
          </p>

          <p className="text-gray-300">搜索你想要的Github Developer</p>
        </div>
        <div
          ref={ref}
          style={{
            height: hide ? 43 : "auto",
            filter: "drop-shadow(0 0 10px #fff)",
          }}
          className="mt-12 mx-auto  rounded-3xl  transition-all duration-[1500ms] bg-white max-w-lg shadow-sm hover:shadow-md "
        >
          <form onSubmit={(e) => e.preventDefault()}>
            <Input
              variant="borderless"
              style={{
                width: "100%",
                height: 43,
              }}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onClick={() => {
                setHide(false);
                startAnimation(true);
              }}
              placeholder="Github"
              suffix={
                loading ? (
                  <LoadingOutlined
                    style={{
                      fontSize: 20,
                    }}
                  />
                ) : (
                  <SearchOutlined
                    style={{
                      fontSize: 20,
                    }}
                  />
                )
              }
            />
          </form>
        </div>
      </div>
    </main>
  );
};

export default Home;
