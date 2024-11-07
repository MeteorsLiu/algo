import { Divider } from "antd";

const Footer = () => {
  return (
    <footer className="transition-all duration-300 py-8 w-full text-slate-400 text-sm bg-black/30  hover:bg-black backdrop-blur-3xl relative clear-both">
      <div className=" mx-auto w-3/4 ">
        <div className="flex flex-col lg:flex-row items-center justify-between">
          <div className="flex flex-row gap-x-4 items-center lg:order-1 order-3">
            <span className="text-white">Github Rank</span>
            <Divider type="vertical" className=" bg-slate-400" />
            <a href="">首页</a>
            <Divider type="vertical" className=" bg-slate-400" />
            <a href=""> 我们团队</a>
          </div>

          <div className=" order-2">Made with ❤ by HelloWorld</div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
