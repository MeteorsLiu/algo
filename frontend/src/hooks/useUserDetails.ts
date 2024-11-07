import { useRequest } from "ahooks";

function useUserDetails(name?: string) {
  const {
    data: userDetails,
    loading: detailLoading,
    run: getUserDetails,
  } = useRequest(
    async () => {
      if (!name) return;
      const res = await fetch(
        `https://api.jellyqwq.top/search/user?q=${name}`,
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
      manual: true,
    }
  );

  return { getUserDetails, userDetails, detailLoading };
}

function useUserAbility(name?: string) {
  const {
    data: userAbility,
    loading: ablityLoading,
    run: getUserAbility,
  } = useRequest(
    async () => {
      if (!name) return;
      const res = await fetch(
        `https://api.jellyqwq.top/search/lang?q=${name}`,
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
      manual: true,
    }
  );

  return { userAbility, ablityLoading, getUserAbility };
}

function useUserRank(name?: string) {
  const {
    data: userRank,
    loading: rankLoading,
    run: getUserRank,
  } = useRequest(
    async () => {
      if (!name) return;
      const res = await fetch(`https://api.jellyqwq.top/${name}/rank`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      }).then((res) => res.json());
      return { data: res };
    },
    {
      manual: true,
    }
  );

  return { userRank, rankLoading, getUserRank };
}

export { useUserAbility, useUserDetails, useUserRank };
