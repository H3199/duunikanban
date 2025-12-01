import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchJobs, updateJobState } from "../api/jobsApi";

export function useJobs(filter?: string) {
  const queryClient = useQueryClient();

  const jobs = useQuery({
    queryKey: ["jobs", filter], // include filter in key
    queryFn: () => fetchJobs(filter), // pass filter into API call
  });

  const setStateMutation = useMutation({
    mutationFn: ({ id, state }: { id: string; state: string }) =>
      updateJobState(id, state),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
    },
  });

  return { jobs, setStateMutation };
}
