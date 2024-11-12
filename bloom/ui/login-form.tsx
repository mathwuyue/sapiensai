"use client";

import { Box, Button, Card, Flex, Text, TextField } from "@radix-ui/themes";
import { useRouter } from "next/navigation";
export default function LoginForm() {
  const router = useRouter();
  return (
    <Box className="p-4">
      <Flex direction="column" align="center" justify="center" height="100vh">
        <Card className="w-[95%] sm:w-full sm:max-w-md">
          <Flex
            direction="column"
            align="center"
            justify="center"
            gap="5"
            className="p-6"
          >
            <Text as="div" size="5" weight="bold">
              Welcome to Bloom
            </Text>
            <TextField.Root
              className="w-full"
              placeholder="Enter your email"
            ></TextField.Root>
            <TextField.Root
              className="w-full"
              type="password"
              placeholder="Enter your password"
            ></TextField.Root>
            <Flex direction="row" gap="3" className="w-full">
              <Button className="w-full">Log In</Button>
              <Button
                variant="outline"
                className="w-full"
                onClick={() => router.push("/signup")}
              >
                Sign Up
              </Button>
            </Flex>
          </Flex>
        </Card>
      </Flex>
    </Box>
  );
}
