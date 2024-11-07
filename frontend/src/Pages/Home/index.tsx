import { Input } from "antd";

import {
  LoadingOutlined,
  RightOutlined,
  SearchOutlined,
  UsergroupDeleteOutlined,
} from "@ant-design/icons";
import { useClickAway, useRequest } from "ahooks";
import { useSetAtom } from "jotai";
import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { backgroundState } from "../../hooks/useBackground";
import "./index.css";

const UserItem = ({ item }: { item: any }) => {
  const nav = useNavigate();
  const [hover, setHover] = useState(false);

  return (
    <div
      onClick={() => nav(`/rank/${item.username}`)}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      className="h-5 w-full flex flex-row rounded rounded-l-none justify-between p-4 items-center cursor-pointer hover:bg-black/20 transition-all"
    >
      <div className="flex flex-row gap-2 text-sm items-center max-w-[80%] text-wrap">
        <UsergroupDeleteOutlined />
        {item.username}
      </div>
      <div
        style={{
          opacity: hover ? 1 : 0,
        }}
        className=" transition-all"
      >
        <RightOutlined />
      </div>
    </div>
  );
};

const Home = () => {
  const nav = useNavigate();
  const ref = useRef<HTMLDivElement | null>(null);
  const startAnimation = useSetAtom(backgroundState);
  const [hide, setHide] = useState(true);
  const [input, setInput] = useState("");

  useClickAway(() => {
    setHide(true);
    startAnimation(false);
  }, ref);

  const { data, loading } = useRequest(
    async () => {
      if (!input) return;
      const res = await fetch(
        `https://api.jellyqwq.top/search/user?q=${input}`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        }
      ).then((res) => res.json());
      return { data: res };
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

            filter:
              hide || !data
                ? "drop-shadow(0 0 10px #fff)"
                : "drop-shadow(0 0 3px #fff)",
          }}
          className="mt-12 overflow-y-auto mx-auto rounded-3xl  transition-all duration-[1500ms] bg-white max-w-lg shadow-sm hover:shadow-md "
        >
          <Input
            variant="borderless"
            className=" !text-black"
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
                  className=" text-blue-500"
                />
              ) : (
                <SearchOutlined
                  style={{
                    fontSize: 20,
                  }}
                  className=" text-black"
                  onClick={() => nav(`/rank/${input}`)}
                />
              )
            }
          />
          {!hide && data && (
            <div className="max-h-[300px] overflow-y-auto">
              {data.data.map((val) => (
                <UserItem item={val} />
              ))}
            </div>
          )}
        </div>
      </div>
    </main>
  );
};

export default Home;
