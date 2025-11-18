import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getJobs, updateJobState } from "../api/jobsApi";

export function useJobs() {
  const qc = useQueryClient();

  const jobs = useQuery({
    queryKey: ["jobs"],
    queryFn: getJobs,
  });

  const setStateMutation = useMutation({
    mutationFn: ({ id, state }: { id: number; state: string }) =>
      updateJobState(id, state),
    onSuccess: () => qc.invalidateQueries(["jobs"]),
  });

  return { jobs, setStateMutation };
}
