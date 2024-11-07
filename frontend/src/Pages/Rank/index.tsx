import {
  AreaChartOutlined,
  LeftCircleFilled,
  LoadingOutlined,
  QuestionCircleOutlined,
  UserOutlined,
} from "@ant-design/icons";
import {
  Card,
  Menu,
  message,
  Progress,
  Space,
  Spin,
  Statistic,
  Table,
  Tooltip,
  Typography,
} from "antd";
import { ReactNode, useEffect, useMemo, useState } from "react";

import { motion } from "framer-motion";
import { Navigate, useNavigate, useParams } from "react-router-dom";
import { useUserDetails } from "../../hooks/useUserDetails";
import "./index.css";

const getGeo = (data: any) => {
  if (!data) return null;

  if (typeof data === "object") return data.nation;

  if (typeof data === "string") {
    if (data.includes("+08")) return "中国";
    if (data.toLowerCase().includes("china")) return "中国";
    return data;
  }

  return null;
};

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

const Person = ({ data }: { data: any }) => {
  const params = useParams();
  const score = useMemo(() => {
    if (data.rank > 0.2758) {
      return "A";
    } else if (data.rank < 0.2758 && data.rank > 0.0412) {
      return "B";
    } else if (data.rank < 0.0412 && data.rank > -0.1102) {
      return "C";
    } else {
      return "D";
    }
  }, [data]);

  const RankTip = () => (
    <>
      该用户评分为：{data.rank}
      <br />
      Talent Rank大于 0.2758 是 A
      <br />
      介于 0.2758 0.0412 之间是 B
      <br />
      介于 0.0412 -0.1102 之间是 C
      <br />
      小于 -0.1102 是 D
    </>
  );
  return (
    <div className="grid grid-cols-3 gap-4 w-full">
      <Card className="neon-card transition-all  hover:scale-105">
        <Statistic
          title="国籍"
          value={getGeo(data.geo) ? getGeo(data.geo) : "未知"}
        ></Statistic>
        {data.geo_prob && (
          <span className="text-slate-300">
            可信度：{Math.floor(data.geo_prob * 100)}%
          </span>
        )}
      </Card>

      <Card className="neon-card transition-all  hover:scale-105">
        <Statistic title="PR数量" value={data.pr_count}></Statistic>
      </Card>

      <Card className="neon-card transition-all  hover:scale-105">
        <Statistic title="Issues数量" value={data.issue_count}></Statistic>
      </Card>

      <Card className=" col-span-3">
        <Typography.Text type="secondary">
          开发者(Talent Rank)评分
          <Tooltip
            title={<RankTip />}
            overlayInnerStyle={{
              width: "300px",
            }}
          >
            <QuestionCircleOutlined className="pl-px" />
          </Tooltip>
          :
        </Typography.Text>
        <h1 className=" text-3xl font-bold">{score}</h1>

        <h1 className="pt-8 pb-4 font-lg">参评项目</h1>
        <Table
          columns={[
            {
              dataIndex: "full_name",
              title: "项目名称",
              key: "full_name",
            },
            {
              dataIndex: "repo_rank",
              title: "项目评分",
              key: "repo_rank",
              sorter: (a, b) => a.repo_rank - b.repo_rank,
            },
            {
              dataIndex: "user_prop",
              title: "贡献度",
              key: "user_prop",
              sorter: (a, b) => a.user_prop - b.user_prop,
            },
          ]}
          dataSource={data.rank_repos}
        />
      </Card>
    </div>
  );
};

const Nation = ({ data }: { data: any }) => {
  return (
    <div className="grid grid-cols-3 gap-4 w-full">
      <Card className="neon-card transition-all  hover:scale-105">
        <Statistic title="国籍" value="中国"></Statistic>
      </Card>
      <Card className="neon-card transition-all  hover:scale-105">
        <Statistic title="国籍" value="中国"></Statistic>
      </Card>
    </div>
  );
};

const conicColors = {
  "0%": "#87d068",
  "50%": "#ffe58f",
  "100%": "#ffccc7",
};

const Ability = ({ data }: { data: any }) => {
  return (
    <div className="grid grid-cols-3 gap-4 w-full">
      <Card className="neon-card transition-all  hover:scale-105">
        <Typography.Title level={3}>使用语言</Typography.Title>
        <div className="flex flex-col gap-1">
          {Object.keys(data.lang).map((key) => (
            <>
              <Typography.Text type="secondary">{key}</Typography.Text>
              <Progress
                format={(percent) => percent}
                percent={data.lang[key]}
                strokeColor={conicColors}
              />
            </>
          ))}
        </div>
      </Card>
      <Card className="neon-card transition-all  hover:scale-105 max-h-fit">
        <Typography.Title level={3}>领域排名</Typography.Title>
        <div className="flex flex-col gap-1">
          {Object.keys(data.lang).map((key) => {
            console.log(data[`rank_${key}`]);
            return (
              <Space>
                <Typography.Text type="secondary">{key}:</Typography.Text>
                <Typography.Text>{data[`rank_${key}`]}</Typography.Text>
              </Space>
            );
          })}
        </div>
      </Card>
    </div>
  );
};

const Rank = () => {
  const nav = useNavigate();
  const params = useParams();
  const [selected, setSelected] = useState("个人分析");
  const [collapsed, setCollapsed] = useState(false);

  const {
    detailLoading: loading,
    userDetails,
    getUserDetails,
  } = useUserDetails(params.name);

  useEffect(() => {
    if (params.name) {
      getUserDetails();
    }
  }, [params.name]);

  if (
    !params.name ||
    (userDetails &&
      (userDetails.data.length == 0 ||
        userDetails.data[0].username != params.name))
  ) {
    message.warning("用户名好像不存在哦");
    return <Navigate to="/" />;
  }

  return (
    <main className="relative flex-1 w-full flex flex-row text-white ">
      <aside
        style={{
          width: collapsed ? 80 : 256,
        }}
        className="!bg-[#001529] shadow-sm transition-all overflow-y-auto overflow-x-hidden  max-h-full relative border-r  border-[#1f2937]"
      >
        {!collapsed && (
          <a
            onClick={() => nav("/")}
            className=" inline-block w-full py-5 mb-2 px-4 font-semibold border-[#1f2937] border-b cursor-pointer"
          >
            Github Rank
          </a>
        )}
        <Menu
          defaultSelectedKeys={["1"]}
          mode="inline"
          theme="dark"
          inlineCollapsed={collapsed}
          selectedKeys={[selected]}
          onSelect={(e) => setSelected(e.key)}
          className="px-2 m-0"
          items={[
            { key: "个人分析", icon: <UserOutlined />, label: "个人分析" },
            { key: "领域分析", icon: <AreaChartOutlined />, label: "领域分析" },
          ]}
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

      {loading && (
        <Spin
          spinning={true}
          size="large"
          className="flex-1 flex justify-center items-center "
          indicator={<LoadingOutlined className=" text-[70px]" />}
        ></Spin>
      )}
      {userDetails && userDetails.data.length > 0 && (
        <div className="p-6 flex flex-col flex-1 gap-y-8">
          <Space>
            <Title>{params.name}</Title>
            <h1 className="  text-base flex items-end  h-[48px] tracking-wide">
              {selected}
            </h1>
          </Space>
          {selected == "个人分析" && <Person data={userDetails.data[0]} />}
          {selected == "领域分析" && <Ability data={userDetails.data[0]} />}
        </div>
      )}
    </main>
  );
};

export default Rank;
